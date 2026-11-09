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

**Not bundled:** proprietary Chinese-market source observations (including Shandong), private Base caches, secrets, credentials, protected test labels, model checkpoints lacking release approval. Obtain public foreign-market data from its original publisher and verify usage rights.

No public GitHub repository has been created or uploaded by this scaffold. See `docs/PROVENANCE.md` before release. This project is intentionally separate from the full `solar_leak_price_model` research repository. Licensing and data redistribution require the authors' decision.
