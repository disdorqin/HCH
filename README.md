# HCH — History-Calibrated Horizon Repair

Source-aligned research artifact for lightweight repair of **already-issued, frozen** 24-hour forecasts. The method uses eligible historical forecast–outcome pairs, a 7-day history encoder, chronologically out-of-fit direction evidence, and a single nonnegative calibrated correction distance.

**Status: prototype release scaffold, NOT a full reproduction package.** The modules here implement the core inference and calibration contract and are validated against the frozen scientific implementation. The chronological optimizer, market-specific loaders, data licenses, baseline replays, and all-paper-table reproduction scripts are still release gates. Do not claim that running the current repository reproduces the 44-cell results.

## Quick verification

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python scripts/release_audit.py
```

The first test compares the published network's forward computation against the hash-locked source file when `HCH_SOURCE_ROOT` (or its recorded local path) is available. It does not read private market data or train a forecast.

## Layout

```text
src/hch/
  model.py         Frozen GRU-32 directional architecture
  data_loader.py   Publishable forecast-cache schema / role checks
  evidence.py      Point-in-time history representation
  calibration.py   OOF weighted-median distance / additive repair
  capacity.py      Chronological block and inner-tail rules
data/              Dataset acquisition instructions; NO private observations
tests/             Mathematical and freeze-equivalence checks
scripts/           Local release audit
docs/              Source provenance and publication gates
```

## Reproduction input contract

A replay cell requires a frozen Base forecast `[N,24]`, revealed historical observations `[N,168]`, historical Base residuals/masks `[N,168]`, forecast origin timestamps, and issue-time-known future state `[N,24,C]`. Fit and evaluation roles must be chronological, disjoint, and originate from the same frozen Base identity. Evaluation targets are only used for offline scoring.

**Bundled foreign-market data:** the source-attributed [Australia AEMO NEM South Australia 2024 hourly dataset](data/foreign/NEM_SA1/SA1_2024_hourly.csv) and its [provenance](data/foreign/NEM_SA1/README.md) are available in this private repository. [Other foreign markets](data/foreign/README.md) remain linked to original sources where independent redistribution permission is absent. **Not bundled:** Chinese-market source observations, private Base caches, secrets, protected test labels or unapproved checkpoints.

This repository exists but is currently **private**; the SA1 dataset has been uploaded, whereas full code and benchmark releases remain subject to audit. See `docs/PROVENANCE.md` before release. This project is intentionally separate from the full `solar_leak_price_model` research repository. Licensing and data redistribution require the authors' decision.
