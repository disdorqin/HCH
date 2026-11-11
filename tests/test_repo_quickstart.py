"""Exercise the documented ICDE-style repository quickstart and CLI scoring."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from hch.data_loader import load_issued_cache

ROOT = Path(__file__).resolve().parents[1]


def test_quickstart_generates_separate_target_free_files_and_cli_scores(tmp_path):
    path = ROOT / "examples" / "quickstart.py"
    spec = importlib.util.spec_from_file_location("hch_public_quickstart", path)
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    summary = example.run(tmp_path, rail=(0,))
    assert summary["status"].startswith("SYNTHETIC")
    assert summary["train_origins"] == 80
    assert summary["eval_origins"] == 5
    assert set(summary["selected_steps"]) == {
        "OOF_B1", "OOF_B2", "OOF_B3", "OOF_B4", "FINAL"
    }
    # If real targets sneak into issued caches, the loader must fail.
    train = load_issued_cache(tmp_path / "fit_issued.npz")
    evaluation = load_issued_cache(tmp_path / "eval_issued.npz")
    assert (train.split == "TRAIN").all()
    assert (evaluation.split == "TEST").all()
    assert len(evaluation.origin_time) == 5
    with np.load(tmp_path / "eval_issued.npz", allow_pickle=False) as src:
        assert "y_true" not in src.files

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "hch_cli.py"),
        "score",
        "--prediction", str(tmp_path / "predictions.npz"),
        "--truth", str(tmp_path / "eval_truth.npz"),
    ]
    result = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, check=True, timeout=60
    )
    scored = json.loads(result.stdout)
    assert scored["type"] == "offline_metric_replay"
    assert scored["n_hours"] == 5 * 24
    assert np.isclose(
        scored["repaired_mae"], summary["offline_synthetic_metrics"]["repaired_mae"]
    )
