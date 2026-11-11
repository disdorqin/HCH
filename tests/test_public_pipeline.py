"""Contract/serialization tests of the author-independent public entrypoint."""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
sys.path.insert(0, str(ROOT/"scripts"))

from hch.data_loader import IssuedForecastCache
from hch.pipeline import fit_hch,predict_issued,save_bundle,load_bundle
from hch_cli import summarize, read_truth


def fixture(n, start, role="TRAIN"):
    t=np.asarray(pd.date_range(start, periods=n, freq="D").astype(str))
    days=np.arange(n)[:,None]
    h=np.repeat(100+days/10,168,axis=1).astype(float)
    r=np.full_like(h,np.nan)
    m=np.zeros_like(h,bool)
    r[:,-48:]=0.5
    m[:,-48:]=True
    b=np.repeat(100+days/10,24,axis=1).astype(float)
    state=np.zeros((n,24,1),float)
    return IssuedForecastCache(b,h,r,m,state,t,np.asarray([role]*n),
                               "SYNTHETIC_ONLY","DEMO_BASE")


def test_fit_bundle_issuance_roundtrip_and_no_future_predictions(tmp_path):
    fit=fixture(60,"2025-01-01")
    targets=fit.issued_forecast+0.5
    bundle=fit_hch(fit,targets,checkpoint_rail=(0,),seed=7)
    assert set(bundle.selected_steps)=={"OOF_B1","OOF_B2","OOF_B3","OOF_B4","FINAL"}
    assert all(k==0 for k in bundle.selected_steps.values())
    assert bundle.alpha>=0
    eval_cache=fixture(4,"2025-04-01",role="TEST")
    pred=predict_issued(bundle,eval_cache)
    assert pred.shape==(4,24)
    out=tmp_path/"bundle.npz"
    save_bundle(bundle,out)
    recovered=load_bundle(out)
    assert np.array_equal(predict_issued(recovered,eval_cache),pred)
    assert recovered.base_id=="DEMO_BASE"
    with pytest.raises(ValueError,match="follow final fitting"):
        predict_issued(bundle,fit)


def test_train_only_and_matching_base_guards():
    f=fixture(60,"2025-01-01",role="TEST")
    with pytest.raises(ValueError,match="TRAIN-only"):
        fit_hch(f,f.issued_forecast)
    f=fixture(60,"2025-01-01")
    b=fit_hch(f,f.issued_forecast+0.5,checkpoint_rail=(0,))
    ev=fixture(2,"2025-04-01",role="TEST")
    changed=IssuedForecastCache(ev.issued_forecast,ev.history_price,ev.history_residual,
          ev.residual_available,ev.future_state,ev.origin_time,ev.split,"OTHER",ev.base_id)
    with pytest.raises(ValueError,match="identity mismatch"):
        predict_issued(b,changed)


def test_target_file_origin_alignment_and_native_metrics(tmp_path):
    origins=np.asarray(["2025-01-01","2025-01-02"])
    path=tmp_path/"target.npz"
    truth=np.ones((2,24),dtype=float)
    np.savez(path,origin_time=origins,y_true=truth)
    assert np.array_equal(read_truth(str(path),origins),truth)
    with pytest.raises(ValueError,match="origin"):
        read_truth(str(path),origins[::-1])
    z=summarize(np.zeros_like(truth),truth.copy(),truth)
    assert z["base_mae"]==1.0 and z["repaired_mae"]==0.0
    assert z["n_hours"]==48
