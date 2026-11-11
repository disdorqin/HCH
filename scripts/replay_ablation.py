"""Replay the *reported* pooled Table III from authorized 24-cell summaries.

Input is an already-computed, seed-aggregated CSV with columns:
variant, market, host, MAE, Base_MAE, relative_MAE, n_seeds.
This script never trains a model and cannot reproduce the raw seed predictions.
"""
from __future__ import annotations
import argparse
import json
import pandas as pd
import numpy as np

REQUIRED={"variant","market","host","MAE","Base_MAE","relative_MAE","n_seeds"}
LABELS=("Full HCH","Direction replacement","Fixed distance","Fixed scale","No CACC")

def summarize(path):
    df=pd.read_csv(path)
    if set(df.columns)!=REQUIRED:
        raise ValueError("unexpected column set in 24-cell reported ablation")
    if set(df.variant)!=set(LABELS):
        raise ValueError("five registered intervention/Full arms required, no extras")
    if not np.all(df.n_seeds==5):
        raise ValueError("this registered panel uses five seeds")
    if df[["MAE","Base_MAE","relative_MAE"]].isna().any().any() or (df.Base_MAE<=0).any():
        raise ValueError("nonfinite or nonpositive base metric")
    calc=100*df.MAE/df.Base_MAE
    if not np.allclose(calc,df.relative_MAE,atol=1e-7,rtol=0):
        raise ValueError("base-normalized metric disagrees with source MAE")
    keys=None
    table={}
    for variant in LABELS:
        sub=df[df.variant==variant]
        cells=set(map(tuple,sub[["market","host"]].to_numpy()))
        if len(sub)!=24 or len(cells)!=24:
            raise ValueError(f"{variant}: expected 24 unique market/Host cells")
        if keys is None:keys=cells
        if cells!=keys:raise ValueError("arms use unmatched market/Host subsets")
        table[variant]=float(sub.relative_MAE.mean())
    full=table["Full HCH"]
    table["Base"]=100.0  # Reference reconstructed from each cell denominator.
    return [{"variant":v,"MAE_pct_Base":table[v],
             "delta_vs_Full_pp":table[v]-full} for v in ("Base",)+LABELS]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,help="authorized source-aggregated CSV; not model predictions")
    a=p.parse_args()
    print(json.dumps({"source_type":"five-seed reported cell summaries, no fit",
                      "rows":summarize(a.input)},indent=2))

if __name__=="__main__":main()
