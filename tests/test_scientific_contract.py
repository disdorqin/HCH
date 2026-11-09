"""Core scientific-contract tests. No source datasets, labels or checkpoints are read."""
from __future__ import annotations
import ast,hashlib,os,pathlib,sys
import numpy as np
import pandas as pd
import pytest
import torch
from torch import nn

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from hch import DailyPatchShape, calibrated_distance, apply_repair,build_evidence,chronological_blocks,inner_split
from hch.model import signed_direction
from hch.calibration import nonnegative_lower_weighted_median

FREEZE_SHA="419ad33405fbcbcba27de92c31524ece140cf576b8a9e28b984276fbf9f52983"

def test_direction_model_architecture_and_parameter_counts():
    for state_dim in (0,1,4,7,9):
        m=DailyPatchShape(state_dim)
        assert sum(p.numel() for p in m.parameters())==13336+768*state_dim
        scores=m(torch.zeros((2,624)),torch.zeros((2,24*state_dim)),torch.zeros((2,96)))
        assert tuple(scores.shape)==(2,24)
        u=signed_direction(scores)
        assert torch.all(torch.linalg.vector_norm(u,dim=1)<=1+1e-6)

def test_chronology_and_capacity_boundaries():
    b=chronological_blocks(140)
    assert len(b["B0"])==56
    assert all(np.max(b[f"B{k-1}"])<np.min(b[f"B{k}"]) for k in range(1,5))
    t,v=inner_split(np.arange(40))
    assert len(t)==32 and len(v)==8 and max(t)<min(v)
    with pytest.raises(ValueError):inner_split(np.arange(19))

def test_weighted_median_and_no_repair_on_missing_history():
    r=np.zeros((3,24),dtype=float)
    u=np.zeros_like(r);u[:,0]=1
    r[:,0]=[0.5,1.5,1.5]
    a=calibrated_distance(r,np.ones(3),u)
    assert a==1.5
    assert nonnegative_lower_weighted_median([-4,-1],[1,5])==0.0
    issued=np.ones((3,24))
    result=apply_repair(issued,u,[1.0,float("nan"),2.0],a)
    assert result[0,0]==2.5
    assert np.array_equal(result[1],issued[1])
    assert result[2,0]==4.0

def test_evidence_masks_and_native_scale():
    n=2
    history=np.ones((n,168),dtype=float)*100
    r=np.full((n,168),np.nan)
    mask=np.zeros((n,168),dtype=bool)
    r[0,-24:]=[(-1.0)**i*2 for i in range(24)]
    mask[0,-24:]=True
    state=np.zeros((n,24,2))
    ev=build_evidence(history,r,mask,np.ones((n,24))*120,
                      pd.to_datetime(["2026-01-02","2026-01-03"]),state,1e-5)
    assert ev.x.shape==(n,624)
    assert ev.future_state.shape==(n,48)
    assert ev.scale[0]==2
    assert np.isnan(ev.scale[1])
    assert np.all(ev.x[1,168:336]==0)
    with pytest.raises(ValueError):
        build_evidence(history,np.zeros_like(r),mask,np.ones((n,24)),
            pd.to_datetime(["2026-01-02","2026-01-03"]),state,1e-5)



def test_public_cache_loader_rejects_target_and_bad_history(tmp_path):
    from hch.data_loader import load_issued_cache
    n=2
    z=dict(
        issued_forecast=np.ones((n,24)),history_price=np.ones((n,168)),
        history_residual=np.full((n,168),np.nan),
        residual_available=np.zeros((n,168),bool),
        future_state=np.zeros((n,24,0)),origin_time=np.array(["2026-01-01","2026-01-02"]),
        split=np.array(["TRAIN","VAL"]),market=np.array("DE"),base_id=np.array("PatchTST"),
    )
    f=tmp_path/"issued.npz"
    np.savez(f,**z)
    c=load_issued_cache(f)
    assert c.issued_forecast.shape==(n,24) and c.base_id=="PatchTST"
    np.savez(f,**z,y_true=np.zeros((n,24)))
    with pytest.raises(ValueError,match="undeclared"):
        load_issued_cache(f)

def test_frozen_runner_neural_forward_when_source_available():
    source=pathlib.Path(os.environ.get("HCH_SOURCE_ROOT",
        str(ROOT.parent.parent/"solar_leak_price_model")))
    runner=source/"experiments/current/hch_s1_sequential_surgical_repair_20260918/implementation/runner.py"
    if not runner.exists():
        pytest.skip("Author's freeze source unavailable; run with HCH_SOURCE_ROOT to verify equivalence")
    digest=hashlib.sha256(runner.read_bytes()).hexdigest()
    assert digest==FREEZE_SHA,"FROZEN_HCH_S1_B2_HASH_MISMATCH"
    node=next(x for x in ast.parse(runner.read_text(encoding="utf8")).body
              if isinstance(x,ast.ClassDef) and x.name=="DailyPatchShape")
    env={"torch":torch,"nn":nn}
    exec(compile(ast.Module(body=[node],type_ignores=[]),filename=str(runner),mode="exec"),env)
    authoritative=env["DailyPatchShape"]
    for nstate in (0,7,9):
        torch.manual_seed(17)
        a=authoritative(nstate);b=DailyPatchShape(nstate)
        b.load_state_dict(a.state_dict())
        torch.manual_seed(19)
        x=torch.randn(3,624)
        state=torch.randn(3,nstate*24)
        calendar=torch.randn(3,96)
        with torch.no_grad():
            x1=a(x,state,calendar);x2=b(x,state,calendar)
        assert torch.equal(x1,x2)
