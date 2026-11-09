"""Read a released issued-forecast cache without unpickling or target access.

This is a schema gate only. The data provider must separately certify issue-time
availability and non-overlap of training / evaluation roles.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass(frozen=True)
class IssuedForecastCache:
    issued_forecast: np.ndarray
    history_price: np.ndarray
    history_residual: np.ndarray
    residual_available: np.ndarray
    future_state: np.ndarray
    origin_time: np.ndarray
    split: np.ndarray
    market: str
    base_id: str

REQUIRED = frozenset({
    "issued_forecast","history_price","history_residual",
    "residual_available","future_state","origin_time","split","market","base_id",
})
FORBIDDEN = frozenset({
    "y_true","target","test_target","future_actual","current_residual",
    "realized_price","heldout_truth",
})

def load_issued_cache(path: str | Path) -> IssuedForecastCache:
    """Load only declared, target-free arrays from an explicitly supplied NPZ path.

    The loader rejects unexpected keys, pickle objects, and duplicate origins
    within each market/Base/split combination. It never builds private data.
    """
    with np.load(Path(path), allow_pickle=False) as src:
        keys = set(src.files)
        unexpected = keys - REQUIRED
        if unexpected:
            raise ValueError(f"undeclared or target-containing cache keys: {sorted(unexpected)}")
        if REQUIRED - keys:
            raise ValueError(f"missing required fields: {sorted(REQUIRED - keys)}")
        fields = {key: src[key] for key in REQUIRED}

    n = len(fields["issued_forecast"])
    issued = np.asarray(fields["issued_forecast"], dtype=np.float64)
    hist = np.asarray(fields["history_price"], dtype=np.float64)
    resid = np.asarray(fields["history_residual"], dtype=np.float64)
    avail = np.asarray(fields["residual_available"], dtype=np.bool_)
    state = np.asarray(fields["future_state"], dtype=np.float64)
    origins = np.asarray(fields["origin_time"]).astype(str)
    roles = np.asarray(fields["split"]).astype(str)
    if issued.shape != (n, 24) or hist.shape != (n,168) or resid.shape != hist.shape or avail.shape != hist.shape:
        raise ValueError("forecast must be [N,24] and history arrays [N,168]")
    if state.ndim != 3 or state.shape[:2] != (n,24) or origins.shape != (n,) or roles.shape != (n,):
        raise ValueError("invalid future-state, origin, or split shape")
    if any(role not in {"TRAIN", "VAL", "TEST", "DEV_EVAL", "POST_TRAIN", "PROTECTED_FINAL"} for role in roles):
        raise ValueError("unknown chronological data role")
    if any(len(set(origins[roles==role]))!=sum(roles==role) for role in set(roles)):
        raise ValueError("duplicate issue origins within split")
    if not (np.isfinite(issued).all() and np.isfinite(hist).all() and np.isfinite(state).all()):
        raise ValueError("nonfinite published forecasts, historical observations or future states")
    if np.isfinite(resid[~avail]).any() or not np.isfinite(resid[avail]).all():
        raise ValueError("historical residual missingness does not match availability mask")
    market = str(np.asarray(fields["market"]).item())
    base_id = str(np.asarray(fields["base_id"]).item())
    if not market or not base_id or len(market)>128 or len(base_id)>128:
        raise ValueError("missing market or frozen-base identity")
    return IssuedForecastCache(issued,hist,resid,avail,state,origins,roles,market,base_id)
