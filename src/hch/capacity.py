"""Non-leaking chronological block and validation-tail partition rules."""
from __future__ import annotations
import math
import numpy as np

def chronological_blocks(n:int)->dict[str,np.ndarray]:
    if n<5:raise ValueError("too few rows for B0..B4")
    n0=int(np.floor(.4*n))
    rest=np.arange(n0,n)
    out={"B0":np.arange(n0)}
    for k,part in enumerate(np.array_split(rest,4),1):
        out[f"B{k}"]=part
    if any(len(v)==0 for v in out.values()):raise ValueError("empty chronological block")
    return out

def inner_split(indices:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    idx=np.asarray(indices,dtype=int)
    nval=max(5,int(math.ceil(.2*len(idx))))
    ntrain=len(idx)-nval
    if ntrain<15:raise ValueError("inner split leaves fewer than 15 training days")
    return idx[:ntrain],idx[ntrain:]
