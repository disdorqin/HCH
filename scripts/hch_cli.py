"""CLI for source-aligned HCH fitting/inference and strictly separate scoring.

No network access or proprietary dataset download; all files are caller-supplied.
Run from the repository root (install pip -e . first).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from hch.data_loader import IssuedForecastCache, load_issued_cache
from hch.pipeline import fit_hch,load_bundle,predict_issued,save_bundle


def read_truth(path: str, required_origins: np.ndarray)->np.ndarray:
    with np.load(path,allow_pickle=False) as z:
        if set(z.files)!={"origin_time","y_true"}:
            raise ValueError("truth file must contain only origin_time and y_true")
        origins = z["origin_time"].astype(str)
        y=z["y_true"]
    if not np.array_equal(origins,required_origins.astype(str)):
        raise ValueError("truth origins/order do not match the issued forecast cache")
    if y.shape!=(len(required_origins),24) or not np.isfinite(y).all():
        raise ValueError("truth must be finite [N,24]")
    return np.asarray(y,dtype=np.float64)


def summarize(issued, repaired, truth):
    if issued.shape!=repaired.shape or issued.shape!=truth.shape or issued.shape[1]!=24:
        raise ValueError("native metric shape mismatch")
    return {"n_origins":len(issued),"n_hours":24*len(issued),
            "base_mae":float(np.mean(np.abs(truth-issued))),
            "repaired_mae":float(np.mean(np.abs(truth-repaired))),
            "base_rmse":float(np.sqrt(np.mean((truth-issued)**2))),
            "repaired_rmse":float(np.sqrt(np.mean((truth-repaired)**2)))}


def sample_cache(n:int, start:str, *, market:str="SYNTHETIC_ONLY", base:str="DEMO_BASE",
                 role:str="TRAIN"):
    """Synthetic fixture is NOT a paper benchmark, forecast or market result."""
    ts=np.asarray(pd.date_range(start,periods=n,freq="D").astype(str))
    x=np.arange(168,dtype=float)
    origins=np.arange(n,dtype=float)[:,None]
    history=100+np.sin((x[None,:]+origins*24)/18)
    residual=np.full((n,168),np.nan,dtype=float)
    mask=np.zeros((n,168),bool)
    mask[:,-72:]=True
    residual[:,-72:]=1.5*np.sin((x[-72:][None,:]+origins*24)/6)
    base_price=np.asarray(100+np.cos((np.arange(24)[None,:]+origins*24)/20),dtype=float)
    state=np.zeros((n,24,2),dtype=float)
    hour=np.arange(24)[None,:]
    state[:,:,0]=np.cos((origins*24+hour)/20)
    state[:,:,1]=np.sin(hour/12)
    return IssuedForecastCache(base_price,history,residual,mask,state,ts,
                               np.asarray([role]*n),market,base)


def demo():
    fit=sample_cache(80,"2025-01-01")
    dates=np.arange(80,dtype=float)[:,None]
    y=fit.issued_forecast+1.2*np.sin((np.arange(24)[None,:]+dates*24)/8)
    model=fit_hch(fit,y,seed=7,checkpoint_rail=(0,25))
    ev=sample_cache(5,"2025-04-01",role="TEST")
    pred=predict_issued(model,ev)
    print(json.dumps({"mode":"SYNTHETIC DEMO ONLY — not paper evidence",
         "train_origins":len(fit.origin_time),"issued_origins":len(ev.origin_time),
         "selected_steps":model.selected_steps,"alpha":model.alpha,
         "output_shape":list(pred.shape),"finite_output":bool(np.isfinite(pred).all())},indent=2))


def run():
    p=argparse.ArgumentParser(description="HCH issued forecast repair; paper reproduction requires controlled caches")
    sub=p.add_subparsers(dest="mode",required=True)
    sub.add_parser("demo")
    a=sub.add_parser("fit",help="uses TRAIN-only issued cache and separately revealed TRAIN targets")
    a.add_argument("--issued",required=True);a.add_argument("--train-truth",required=True)
    a.add_argument("--output",required=True);a.add_argument("--seed",type=int,default=7)
    b=sub.add_parser("predict",help="NO target input; chronological issue-only inference")
    b.add_argument("--issued",required=True);b.add_argument("--bundle",required=True)
    b.add_argument("--output",required=True)
    c=sub.add_parser("score",help="offline scoring; requires separate target file")
    c.add_argument("--prediction",required=True);c.add_argument("--truth",required=True)
    args=p.parse_args()
    if args.mode=="demo":demo();return
    if args.mode=="fit":
        cache=load_issued_cache(args.issued)
        y=read_truth(args.train_truth,cache.origin_time)
        bundle=fit_hch(cache,y,seed=args.seed)
        save_bundle(bundle,args.output)
        print(json.dumps({"type":"trained_bundle","path":args.output,
                          "alpha":bundle.alpha,"selected_steps":bundle.selected_steps,
                          "source":"caller-authorized TRAIN-only fitting inputs"},indent=2))
    elif args.mode=="predict":
        cache=load_issued_cache(args.issued)
        model=load_bundle(args.bundle)
        pred=predict_issued(model,cache)
        np.savez_compressed(args.output,
                 origin_time=cache.origin_time.astype(str),
                 issued_forecast=cache.issued_forecast,repaired_forecast=pred,
                 market=np.asarray(cache.market),base_id=np.asarray(cache.base_id))
        print(json.dumps({"type":"target-free_prediction","n_origins":len(pred),
                          "output":args.output},indent=2))
    elif args.mode=="score":
        with np.load(args.prediction,allow_pickle=False) as z:
            keys={"origin_time","issued_forecast","repaired_forecast","market","base_id"}
            if set(z.files)!=keys:raise ValueError("prediction schema mismatch")
            origins=z["origin_time"].astype(str)
            base=z["issued_forecast"]
            pred=z["repaired_forecast"]
        y=read_truth(args.truth,origins)
        print(json.dumps({"type":"offline_metric_replay",**summarize(base,pred,y)},indent=2))


if __name__=="__main__":
    try:
        run()
    except (ValueError,FileNotFoundError,KeyError) as e:
        print("HCH input validation failed: "+str(e),file=sys.stderr)
        raise SystemExit(2) from e
