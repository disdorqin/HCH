# Reproducing the HCH method (scope and executable gates)

## 1. Clean local environment

Use Python 3.10+ and preferably a fresh virtual environment. From this repository's root:

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python scripts/hch_cli.py demo
python examples/quickstart.py --output outputs/synthetic_quickstart
python scripts/hch_cli.py score --prediction outputs/synthetic_quickstart/predictions.npz --truth outputs/synthetic_quickstart/eval_truth.npz
python scripts/fetch_epftoolbox.py --dataset DE --dry-run
python scripts/release_audit.py
```

The `demo` command performs full **synthetic-only** chronological fitting: 40% initial prefix, four later OOF blocks, inner-tail minimum-validation selection on the `[0,25]` rail, independent same-initialization refits, the nonnegative lower weighted-median calibration and target-free deployment of one frozen additive correction. Its output is not evidence for the paper's forecast accuracy. The frozen publication rail for real fit is `[0,25,...,1000]`.

## 2. Real cache contract and issue-time boundary

Prepare separate files *outside the Git repository*:
- `fit_issued.npz`: required fields documented in `data/README.md`; `split` must be TRAIN in all rows, issue origins strictly increasing. No target-day `y_true` in this NPZ.
- `fit_truth.npz`: exactly `origin_time` and `y_true[N,24]`, fitting-only labels revealed before the later evaluation period.
- `eval_issued.npz`: same target-free issued schema, later issue origins, identical market and frozen Base identity.
- `eval_truth.npz`: offline scoring only, `origin_time` and `y_true[N,24]`, never loaded by prediction.

```powershell
python scripts/hch_cli.py fit --issued <fit_issued.npz> --train-truth <fit_truth.npz> --output <bundle.npz> --seed 7
python scripts/hch_cli.py predict --issued <eval_issued.npz> --bundle <bundle.npz> --output <predictions.npz>
python scripts/hch_cli.py score --prediction <predictions.npz> --truth <eval_truth.npz>
```

All outputs should be stored in a private or user-authorized external directory. The CLI refuses labels in the issued cache, nonmonotonic origins, Base/market identity mismatches and predictions from fitting-era origins. The loader cannot independently prove original provider publication times; the caller must retain verified input as-of metadata. If any admitted forecast-known state variable cannot be verified at the issue cutoff, do not label the replay as operationally time-legal.

## 3. Obtain source market data (distinct from exact paper reproduction)

```powershell
python scripts/fetch_epftoolbox.py --dataset DE
python scripts/fetch_epftoolbox.py --dataset PJM
python scripts/fetch_epftoolbox.py --dataset NP
```

The original publication dataset is at https://zenodo.org/records/4624805 . Downloading the data alone **does not** create paper-aligned issue-time windows, frozen four-Host predictions, residual histories, publication-time covariate manifests or scientific split labels. Those require the approved original preprocessing/Host caches. No stock synthetic replacement is allowed when claiming an empirical reproduction.

## 4. Scope of the current release

| Item | Status |
| --- | --- |
| 7-day/24-hour GRU32 forward implementation | implemented, frozen-source numeric forward test |
| Historical scale with missing-vs-zero mask | implemented and unit-tested |
| 40% + four-block OOF, inner checkpoint, identical-initialization refit | implemented and synthetic-tested; full-prefix-before-filter state normalization independently regression-tested, no registered market-cache replay |
| One shared nonnegative weighted-median distance per Base and market | implemented and unit-tested |
| Frozen target-free predict + later offline MAE/RMSE | implemented; synthetic demo and contract tests only |
| Original 44-cell paper Table II | **not reproducible from this public tree**: Base/preprocessing/caches missing |
| 24-cell, 5-seed Main Table III and Supplementary paired calibration analysis | reported aggregates and source-audited replay; not a from-scratch public training run |
| Main Table IV (44-cell normalized accuracy and incremental repairer size) | values reported in the manuscript; full real-market Base/baseline cache replay is not yet packaged |
| Baseline exact fidelity and ten-seed comparisons | **not fully packaged**, upstream revisions/licensing and issued prediction caches missing |
| Private Chinese market observations | **not released**, pending institutional authorization |
| Public original EPF CSV acquisition | verified documented URL; local download optional, not incorporated into paper replay |

For the author-side reported Table III replay (no training), the verified local evidence CSV can be checked with `python scripts/replay_ablation.py --input ../paper/final_paper/review/ablation_normalized_cells.csv` when this repository is still inside the HCH author workspace. In a standalone public checkout, supply an independently authorized 24-cell summary CSV with the documented header; raw prediction files are **not** bundled. The script verifies matched cells and recovers the published Base-normalized pooled rows (Full HCH 90.807167%, No CACC 95.584912%).

The outputs of `release_audit.py` intentionally remain NOT READY until the full paper-reproduction gates are met. A passing unit test, demo or aggregate-score replay must never be represented as 44-cell reproduction.
