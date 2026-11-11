# Reproducible quickstart (synthetic only)

This folder provides a **working** isolated demonstration of the HCH source interface. It does not train on or benchmark a real electricity market.

From the repository root after `python -m pip install -e ".[test]"`:

```bash
python examples/quickstart.py --output outputs/synthetic_quickstart
python scripts/hch_cli.py score --prediction outputs/synthetic_quickstart/predictions.npz --truth outputs/synthetic_quickstart/eval_truth.npz
```

The first command fits a source-aligned chronological direction estimator with the **short demo checkpoint rail 0/25**, calibrates one distance, serializes a numeric non-pickle model bundle, and applies it to five later synthetic issuance origins. It writes seven files into the ignored output directory:

| File | Role |
| --- | --- |
| `fit_issued.npz` | Target-free TRAIN-period issued forecasts and historical evidence |
| `fit_truth.npz` | Revealed TRAIN labels, only used for fitting |
| `eval_issued.npz` | Target-free future issued predictions and historical evidence |
| `eval_truth.npz` | Offline-only synthetic outcomes for scoring |
| `bundle.npz` | Frozen weights, state normalization and scalar calibration |
| `predictions.npz` | Issued Base and repaired predictions, no outcomes |
| `example_report.json` | Clearly labeled synthetic run summary |

The second command replays MAE/RMSE by reading the already saved predictions and the separate outcomes. **This example demonstrates software compatibility, not 44-cell or 24-cell manuscript result reproduction.** The registered paper fitting rail is 0,25,...,1000; the short rail is used solely to keep this synthetic example quick.

For actual market data acquisition and known missing Host-cache / as-of-field dependencies, see [data](../data/README.md) and [full reproduction scope](../docs/reproduce.md).
