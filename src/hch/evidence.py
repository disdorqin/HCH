"""Forecast-aligned, observation-availability-aware evidence representation."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Evidence:
    x: np.ndarray                    # [N, 624]: history actual/residual/mask + Base + calendar
    future_state: np.ndarray         # [N, 24*C], for separate chronological normalization
    calendar: np.ndarray             # [N,96]
    scale: np.ndarray                # [N], NaN if historical residual unavailable
    residual_available: np.ndarray   # [N,168]

def build_evidence(history_price,history_residual,residual_available,issued_forecast,
                   origin_time,future_state,scale_floor:float)->Evidence:
    """Make the 624-D frozen input without treating unavailable residuals as zeros.

    Only caller-certified publication-time-eligible `future_state` is permitted.
    This function checks shape and mask but cannot certify upstream release timestamps.
    """
    h=np.asarray(history_price,dtype=np.float64)
    r=np.asarray(history_residual,dtype=np.float64)
    m=np.asarray(residual_available,dtype=bool)
    b=np.asarray(issued_forecast,dtype=np.float64)
    st=np.asarray(future_state,dtype=np.float64)
    if h.ndim!=2 or h.shape[1]!=168 or r.shape!=h.shape or m.shape!=h.shape:
        raise ValueError("historical price, residual and mask must be [N,168]")
    n=len(h)
    if b.shape!=(n,24) or st.ndim!=3 or st.shape[:2]!=(n,24):
        raise ValueError("Base must be [N,24] and future state [N,24,C]")
    if not np.isfinite(h).all() or not np.isfinite(b).all() or not np.isfinite(st).all():
        raise ValueError("observed and issued inputs must be finite")
    if np.isfinite(r[~m]).any() or not np.isfinite(r[m]).all():
        raise ValueError("unrevealed residuals must be NaN; revealed residuals finite")
    if not np.isfinite(scale_floor) or scale_floor<=0:
        raise ValueError("scale_floor must be fitted and positive")
    location=np.median(h,axis=1)
    n_obs=m.sum(axis=1)
    sum_obs=np.where(m,np.abs(np.nan_to_num(r,nan=0.0)),0.0).sum(axis=1)
    valid=n_obs>0
    scale=np.full(n,np.nan,dtype=np.float64)
    scale[valid]=np.maximum(sum_obs[valid]/n_obs[valid],scale_floor)
    denom=np.where(valid,scale,1.)
    hh=(h-location[:,None])/denom[:,None]
    rr=np.where(m,np.nan_to_num(r,nan=0.0)/denom[:,None],0.0)
    bb=(b-location[:,None])/denom[:,None]
    days=[];time=pd.to_datetime(np.asarray(origin_time))
    if len(time)!=n:raise ValueError("origin count must match batch")
    for t in time:
        ts=pd.date_range(t,periods=24,freq="h")
        hour=ts.hour.to_numpy(dtype=np.float64)
        dow=ts.dayofweek.to_numpy(dtype=np.float64)
        days.append(np.stack([np.sin(2*np.pi*hour/24),np.cos(2*np.pi*hour/24),
                              np.sin(2*np.pi*dow/7),np.cos(2*np.pi*dow/7)],axis=1))
    cal=np.asarray(days,dtype=np.float32).reshape(n,96)
    x=np.concatenate([hh,rr,m.astype(np.float64),bb,cal],axis=1).astype(np.float32)
    if x.shape!=(n,624):raise AssertionError("frozen input must have 624 coordinates")
    return Evidence(x,st.reshape(n,-1).astype(np.float32),cal,scale,m)
