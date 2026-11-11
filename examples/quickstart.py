"""Standalone author-safe synthetic HCH quickstart.

Produces separate train/eval target-free issued caches and offline labels, fits
with the short demo rail, writes a numeric checkpoint, predicts, and scores.
The simulated numbers are NEVER a scientific reproduction of the ICDE tables.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hch_cli import sample_cache, summarize
from hch.pipeline import fit_hch, load_bundle, predict_issued, save_bundle


def _write_issued(path: Path, cache) -> None:
    # No y_true in an issued cache: this is also validated by the real CLI.
    fields = dict(vars(cache))
    # Pandas can leave date labels as object dtype; NPZ must be pickle-free.
    fields["origin_time"] = np.asarray(cache.origin_time, dtype="U32")
    fields["split"] = np.asarray(cache.split, dtype="U24")
    np.savez_compressed(path, **fields)


def _write_truth(path: Path, origin_time: np.ndarray, y_true: np.ndarray) -> None:
    np.savez_compressed(path, origin_time=np.asarray(origin_time, dtype="U32"), y_true=y_true)


def run(output_dir: Path, *, rail: tuple[int, ...] = (0, 25)) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fit = sample_cache(80, "2025-01-01", role="TRAIN")
    evaluation = sample_cache(5, "2025-04-01", role="TEST")

    i = np.arange(80, dtype=float)[:, None]
    eval_i = np.arange(5, dtype=float)[:, None]
    y_fit = fit.issued_forecast + 1.2 * np.sin((np.arange(24)[None, :] + i * 24) / 8)
    y_eval = evaluation.issued_forecast + 1.2 * np.sin(
        (np.arange(24)[None, :] + (eval_i + 80) * 24) / 8
    )

    # Physical files exercise the documented input contract and role separation.
    _write_issued(output_dir / "fit_issued.npz", fit)
    _write_truth(output_dir / "fit_truth.npz", fit.origin_time, y_fit)
    _write_issued(output_dir / "eval_issued.npz", evaluation)
    _write_truth(output_dir / "eval_truth.npz", evaluation.origin_time, y_eval)

    bundle = fit_hch(fit, y_fit, seed=7, checkpoint_rail=rail)
    save_bundle(bundle, output_dir / "bundle.npz")
    restored = load_bundle(output_dir / "bundle.npz")

    # Issued prediction depends on cache and frozen bundle only, never on y_eval.
    repaired = predict_issued(restored, evaluation)
    np.savez_compressed(
        output_dir / "predictions.npz",
        origin_time=np.asarray(evaluation.origin_time, dtype="U32"),
        issued_forecast=evaluation.issued_forecast,
        repaired_forecast=repaired,
        market=np.asarray(evaluation.market),
        base_id=np.asarray(evaluation.base_id),
    )
    metrics = summarize(evaluation.issued_forecast, repaired, y_eval)
    payload = {
        "status": "SYNTHETIC SOFTWARE EXAMPLE — NOT HCH PAPER EVIDENCE",
        "train_origins": 80,
        "eval_origins": 5,
        "checkpoint_rail": list(rail),
        "selected_steps": bundle.selected_steps,
        "offline_synthetic_metrics": metrics,
        "output_directory": str(output_dir),
    }
    (output_dir / "example_report.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="outputs/synthetic_quickstart",
        help="Local output directory, ignored by .gitignore",
    )
    args = parser.parse_args()
    print(json.dumps(run(Path(args.output)), indent=2))
