"""Source-aligned, standalone chronological HCH fitting and issuance interface.

This package implements the registered direction-MSE/chronological inner-tail
selection/lower weighted-median algorithm. It is NOT a verified reconstruction
of the complete paper benchmark: source-specific Base caches and data licences
are outside this release. Do not fit on protected evaluation targets.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
import torch

from .calibration import apply_repair, calibrated_distance
from .capacity import chronological_blocks, inner_split
from .data_loader import IssuedForecastCache
from .evidence import build_evidence
from .model import DailyPatchShape, signed_direction

HORIZON = 24
EPS = 1e-8
LR = 1e-3
WD = 1e-4
DEFAULT_RAIL = tuple(range(0, 1001, 25))


@dataclass
class HCHBundle:
    market: str
    base_id: str
    nstate: int
    seed: int
    scale_floor: float
    alpha: float
    state_mean: np.ndarray
    state_std: np.ndarray
    last_fit_origin: str
    selected_steps: dict[str, int]
    parameters: dict[str, np.ndarray]


def _ordered_origins(origins: np.ndarray) -> np.ndarray:
    t = np.asarray(origins).astype("datetime64[ns]")
    if np.isnat(t).any() or len(np.unique(t)) != len(t):
        raise ValueError("origins must be valid and unique")
    if len(t) > 1 and not np.all(t[1:] > t[:-1]):
        raise ValueError("cache origins must be strictly chronological")
    return t


def _floor_from_fit_history(residual: np.ndarray, mask: np.ndarray) -> float:
    """Exact frozen training_residual_floor from available historical residuals."""
    x = np.abs(np.asarray(residual, np.float64)[np.asarray(mask, bool)])
    global_scale = float(x.mean()) if x.size else 1.0
    return max(global_scale * np.finfo(np.float32).eps, np.finfo(np.float32).tiny)


def _state_norm(reference: np.ndarray, candidate: np.ndarray):
    ref = reference.reshape(len(reference), -1)
    other = candidate.reshape(len(candidate), -1)
    mu = ref.mean(axis=0, keepdims=True)
    sd = ref.std(axis=0, keepdims=True) + 1e-6
    return (ref - mu) / sd, (other - mu) / sd, mu.reshape(-1), sd.reshape(-1)


def _target_vectors(revealed_targets: np.ndarray, issued: np.ndarray, scale: np.ndarray):
    resid = revealed_targets - issued
    e = resid / np.where(np.isfinite(scale), scale, 1.0)[:, None]
    e = e.astype(np.float32)
    norms = np.linalg.norm(e, axis=1)
    valid = (norms > 1e-12) & np.isfinite(scale)
    target = np.zeros_like(e)
    target[valid] = e[valid] / norms[valid, None]
    return resid, target, valid


def _fresh(seed: int, nstate: int):
    # Mirrors frozen runner: instantiate, reseed, then recursively reset.
    m = DailyPatchShape(nstate)
    np.random.seed(seed)
    torch.manual_seed(seed)
    for module in m.modules():
        if hasattr(module, "reset_parameters"):
            module.reset_parameters()
    return m


def _forward(m, x, state, cal):
    return m(torch.as_tensor(x, dtype=torch.float32),
             torch.as_tensor(state, dtype=torch.float32),
             torch.as_tensor(cal, dtype=torch.float32))


def _fit_one(x: np.ndarray, state: np.ndarray, cal: np.ndarray,
             target: np.ndarray, valid: np.ndarray,
             ref_index: np.ndarray, pred_x: np.ndarray, pred_state: np.ndarray,
             pred_cal: np.ndarray, nstate: int, seed: int,
             checkpoint_rail: tuple[int, ...]):
    if not checkpoint_rail or checkpoint_rail[0] != 0:
        raise ValueError("checkpoint rail must begin at 0")
    if any(k < 0 or k % 25 for k in checkpoint_rail) or tuple(sorted(set(checkpoint_rail))) != checkpoint_rail:
        raise ValueError("checkpoint rail must be sorted unique multiples of 25")
    # Match frozen fit_base_predict: fit state moments on the complete legal
    # chronological prefix BEFORE excluding undefined/zero direction targets.
    # Ineligible days still determine state normalization, but never enter
    # checkpoint training/validation or the final direction objective.
    full_ref = np.asarray(ref_index, dtype=int)
    sf_all, sp, mu, sd = _state_norm(state[full_ref], pred_state)
    eligible = valid[full_ref]
    ref = full_ref[eligible]
    sf = sf_all[eligible]
    if len(ref) < 20:
        raise ValueError("at least 20 eligible chronological fitting origins required")
    tr, va = inner_split(np.arange(len(ref)))
    initial = copy.deepcopy(_fresh(seed, nstate).state_dict())
    probe = DailyPatchShape(nstate)
    probe.load_state_dict(initial)
    tx, ts, tc, ty = x[ref[tr]], sf[tr], cal[ref[tr]], target[ref[tr]]
    vx, vs, vc, vy = x[ref[va]], sf[va], cal[ref[va]], target[ref[va]]
    def mse(model, a,b,c,t):
        return torch.nn.functional.mse_loss(_forward(model,a,b,c),
                                             torch.as_tensor(t,dtype=torch.float32))
    best = float(mse(probe,vx,vs,vc,vy).detach())
    selected = 0
    if max(checkpoint_rail) > 0:
        opt = torch.optim.AdamW(probe.parameters(),lr=LR,weight_decay=WD)
        rail = set(checkpoint_rail)
        for step in range(1,max(checkpoint_rail)+1):
            opt.zero_grad(set_to_none=True)
            loss = mse(probe,tx,ts,tc,ty)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(probe.parameters(),1.0)
            opt.step()
            if step in rail:
                value = float(mse(probe,vx,vs,vc,vy).detach())
                if value < best - 1e-12:
                    best,selected = value,step
    # The full-prefix refit restarts from the identical initialization.
    final = DailyPatchShape(nstate)
    final.load_state_dict(initial)
    if selected:
        opt = torch.optim.AdamW(final.parameters(),lr=LR,weight_decay=WD)
        for _ in range(selected):
            opt.zero_grad(set_to_none=True)
            loss = mse(final,x[ref],sf,cal[ref],target[ref])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(final.parameters(),1.0)
            opt.step()
    final.eval()
    with torch.no_grad():
        direction = signed_direction(_forward(final,pred_x,sp,pred_cal)).numpy()
    return final,direction,selected,mu,sd


def fit_hch(fit_cache: IssuedForecastCache, fit_targets: np.ndarray, *,
            seed: int = 7, checkpoint_rail: tuple[int,...] = DEFAULT_RAIL) -> HCHBundle:
    """Fit only from chronologically disclosed fitting targets.

    fit_targets must be in a *separate* author-permitted fitting-only file,
    verified by the CLI to share exact origin identities with fit_cache.
    No evaluation target is accepted or loaded by predict_issued().
    """
    _ordered_origins(fit_cache.origin_time)
    if not np.all(fit_cache.split == "TRAIN"):
        raise ValueError("fit_hch accepts TRAIN-only caches; no VAL/TEST/protected labels")
    y = np.asarray(fit_targets,dtype=np.float64)
    if y.shape != fit_cache.issued_forecast.shape or not np.isfinite(y).all():
        raise ValueError("training target shape/values inconsistent with issued Base")
    torch.use_deterministic_algorithms(True)
    nstate=fit_cache.future_state.shape[-1]
    floor=_floor_from_fit_history(fit_cache.history_residual,fit_cache.residual_available)
    ev=build_evidence(fit_cache.history_price,fit_cache.history_residual,
                      fit_cache.residual_available,fit_cache.issued_forecast,
                      fit_cache.origin_time,fit_cache.future_state,floor)
    resid,target,valid=_target_vectors(y,fit_cache.issued_forecast,ev.scale)
    blocks=chronological_blocks(len(y))
    directions=np.full((len(y),24),np.nan,dtype=np.float32)
    selected={}
    for k in range(1,5):
        ref=np.concatenate([blocks[f"B{j}"] for j in range(k)])
        active=blocks[f"B{k}"][np.isfinite(ev.scale[blocks[f"B{k}"]])]
        if len(active)==0:
            raise ValueError(f"B{k} has no eligible OOF origins")
        _,u,step,_,_=_fit_one(ev.x,ev.future_state,ev.calendar,
                        target,valid,ref,ev.x[active],ev.future_state[active],
                        ev.calendar[active],nstate,seed,checkpoint_rail)
        directions[active]=u
        selected[f"OOF_B{k}"]=step
    alpha=calibrated_distance(resid,ev.scale,directions)
    full=np.arange(len(y))
    final,_,step,mu,sd=_fit_one(ev.x,ev.future_state,ev.calendar,target,valid,
                    full,ev.x,ev.future_state,ev.calendar,nstate,seed,checkpoint_rail)
    selected["FINAL"]=step
    return HCHBundle(fit_cache.market,fit_cache.base_id,nstate,seed,floor,alpha,
                     mu,sd,str(fit_cache.origin_time[-1]),selected,
                     {key:p.detach().cpu().numpy().copy() for key,p in final.state_dict().items()})


def predict_issued(bundle: HCHBundle, cache: IssuedForecastCache) -> np.ndarray:
    """Inference contract: consumes only target-free issued cache."""
    if (bundle.market,bundle.base_id)!=(cache.market,cache.base_id):
        raise ValueError("frozen market/Base identity mismatch")
    dates=_ordered_origins(cache.origin_time)
    if np.any(dates <= np.datetime64(bundle.last_fit_origin)):
        raise ValueError("issuance origins must follow final fitting origin")
    if cache.future_state.shape[-1]!=bundle.nstate:
        raise ValueError("incompatible forecast-known state width")
    ev=build_evidence(cache.history_price,cache.history_residual,
                      cache.residual_available,cache.issued_forecast,
                      cache.origin_time,cache.future_state,bundle.scale_floor)
    m=DailyPatchShape(bundle.nstate)
    m.load_state_dict({k:torch.from_numpy(v.copy()) for k,v in bundle.parameters.items()},strict=True)
    m.eval()
    st=(ev.future_state.astype(np.float64)-bundle.state_mean)/bundle.state_std
    with torch.no_grad():
        raw=_forward(m,ev.x,st,ev.calendar)
        direction=signed_direction(raw).numpy()
    return apply_repair(cache.issued_forecast,direction,ev.scale,bundle.alpha)


def save_bundle(bundle: HCHBundle, path: str|Path):
    """Non-pickle numeric NPZ; write outside repository, never commit checkpoints."""
    meta={"market":bundle.market,"base_id":bundle.base_id,
          "nstate":bundle.nstate,"seed":bundle.seed,"scale_floor":bundle.scale_floor,
          "alpha":bundle.alpha,"last_fit_origin":bundle.last_fit_origin,
          "selected_steps":bundle.selected_steps}
    arrays={"meta_json":np.asarray(json.dumps(meta,sort_keys=True)),
            "state_mean":bundle.state_mean,"state_std":bundle.state_std}
    arrays.update({"param__"+k:v for k,v in bundle.parameters.items()})
    np.savez_compressed(path,**arrays)


def load_bundle(path: str|Path)->HCHBundle:
    with np.load(path,allow_pickle=False) as z:
        meta=json.loads(str(z["meta_json"].item()))
        p={key[len("param__"):]:z[key].copy() for key in z.files if key.startswith("param__")}
        mu=z["state_mean"].copy()
        sd=z["state_std"].copy()
    if not np.isfinite(mu).all() or not np.isfinite(sd).all() or (sd<=0).any():
        raise ValueError("checkpoint normalization invalid")
    if not np.isfinite(meta["alpha"]) or meta["alpha"]<0:
        raise ValueError("checkpoint alpha invalid")
    return HCHBundle(meta["market"],meta["base_id"],int(meta["nstate"]),int(meta["seed"]),
                     float(meta["scale_floor"]),float(meta["alpha"]),mu,sd,
                     meta["last_fit_origin"],meta["selected_steps"],p)
