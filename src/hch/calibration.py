"""Chronological OOF scalar calibration and the issue-time additive decision."""
from __future__ import annotations
import numpy as np

def nonnegative_lower_weighted_median(ratios: np.ndarray, weights: np.ndarray) -> float:
    """Exact lower weighted-median solution of min_{a>=0} sum_j w_j*abs(z_j-a).

    Stable mergesort and searchsorted(side="left") match frozen B2's tie convention.
    """
    r=np.asarray(ratios,dtype=np.float64).reshape(-1)
    w=np.asarray(weights,dtype=np.float64).reshape(-1)
    if r.shape != w.shape: raise ValueError("ratio and weight shapes disagree")
    valid=np.isfinite(r)&np.isfinite(w)&(w>0)
    r,w=r[valid],w[valid]
    if not len(r): return 0.0
    order=np.argsort(r,kind="mergesort")
    r,w=r[order],w[order]
    return max(0.0,float(r[np.searchsorted(np.cumsum(w),0.5*w.sum(),side="left")]))

def calibrated_distance(residual: np.ndarray, scale: np.ndarray, oof_direction: np.ndarray) -> float:
    """Source-matched alpha from available historical OOF normalized residuals.

    residual: [N,24], scale: [N], oof_direction: [N,24].
    Fully missing OOF rows are excluded; only |direction|>1e-12 eligible.
    """
    e=np.asarray(residual,dtype=np.float64)
    s=np.asarray(scale,dtype=np.float64)
    u=np.asarray(oof_direction,dtype=np.float64)
    if e.ndim!=2 or e.shape[1]!=24 or u.shape!=e.shape or s.shape!=(len(e),):
        raise ValueError("expected residual/direction [N,24] and scale [N]")
    rows=np.isfinite(u).all(axis=1)&np.isfinite(s)
    if not np.any(rows):return 0.0
    z=np.divide(e[rows]/s[rows,None],u[rows],
                out=np.full_like(u[rows],np.nan),where=u[rows]!=0)
    w=np.abs(u[rows])
    keep=np.isfinite(z)&(w>1e-12)
    return nonnegative_lower_weighted_median(z[keep],w[keep])

def apply_repair(issued_forecast: np.ndarray, direction: np.ndarray, scale: np.ndarray, alpha: float) -> np.ndarray:
    """One native-unit additive correction, with the frozen Base preserved on missing scale."""
    base=np.asarray(issued_forecast,dtype=np.float64)
    u=np.asarray(direction,dtype=np.float64)
    s=np.asarray(scale,dtype=np.float64)
    if base.ndim!=2 or base.shape[1]!=24 or u.shape!=base.shape or s.shape!=(len(base),):
        raise ValueError("expected issued/direction [N,24], scale [N]")
    if not np.isfinite(base).all():raise ValueError("issued Base must be finite")
    if not np.isfinite(u).all():raise ValueError("direction must be finite")
    if not np.isfinite(s[np.isfinite(s)]).all() or alpha<0 or not np.isfinite(alpha):
        raise ValueError("nonnegative finite distance required")
    safe_scale=np.nan_to_num(s,nan=0.0)
    return base+float(alpha)*u*safe_scale[:,None]
