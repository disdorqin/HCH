# Scientific provenance and release gates

## Frozen authority (read-only original)

Source checkout: private author-owned research tree, configured locally through `HCH_SOURCE_ROOT`. No author filesystem path should appear in the public repository.

- Algorithm runner: `experiments/current/hch_s1_sequential_surgical_repair_20260918/implementation/runner.py`, SHA256 `419ad33405fbcbcba27de92c31524ece140cf576b8a9e28b984276fbf9f52983`
- Historical features: `src/mvp/hch_minimal_repair/features.py`, SHA256 `96d83a6a1e540dbacc3c34190c5ea45aa1b39c96a992c92b999e4616c865ca35`
- Chronological block helper: `src/mvp/hch_minimal_repair/crossfit.py`, SHA256 `30beaee8111dfcc59c641866c5ae2ce7e694e70f862fff6e11b51a5bfe0869bd`
- Training helpers: `src/mvp/hch_minimal_repair/training.py`, SHA256 `b1e96af7220ea0229458973b6507cc39ef0bb960c019db7dc42091c2520a9860`
- Freeze authority: `docs/current/HCH_S1_B2_FINAL_CODE_FREEZE_20260919.md`.

**Do not publish `src/mvp/hch_minimal_repair/model.py` as HCH:** it is an older M0 model with an amplitude head and a verifier gate. The chosen B2 method is the stage-local `DailyPatchShape` + OOF scalar implementation from the authoritative runner.

## Current package equivalence limits

`src/hch/model.py` matches the frozen class constructor, feature segmentation and forward path. `calibration.py` reproduces the frozen nonnegative lower weighted-median convention. Unit tests cover controlled numeric equivalence against the frozen runner (when accessible). The target-rejecting public cache schema, chronological TRAIN-only fit, synthetic-issued prediction and separate offline scoring have executable tests. The chronological S1-B2 fitting/OOF/full-refit implementation in `pipeline.py` has a synthetic end-to-end demonstration; it is not yet verified against matched original registered real-market fit/prediction caches.

### Frozen state-normalization order repair (2026-11-11)

The frozen runner's `fit_base_predict` computes forecast-state mean/std from **every row in the legal chronological fitting prefix**, then filters out rows lacking eligible direction targets. The original public `pipeline.py::_fit_one` incorrectly filtered those rows before computing state moments. This has been corrected **only in the public copy**: `sf_all` and prediction-state normalization now use the complete prefix; the eligible mask is subsequently applied to normalized training rows, preserving the frozen inner-tail split and checkpoint rail. The new `tests/test_state_normalization_source_order.py` includes three ineligible rows with intentionally shifted state covariates, directly checks unfiltered-prefix moment arrays and issued directions, and reproduces a 25-step probe, earliest checkpoint choice and identical-initialization final refit in an independent synthetic implementation. These tests demonstrate this specific source-order contract; they do not certify every real-market tensor or ten-seed output.

## Mandatory release gates

1. All frozen SHA checks PASS; no methodology changes in the original research checkout.
2. Test the clean core against original frozen outputs on matched, source-permitted forecast caches, not on invented market data.
3. B0--B4 fitting, inner-tail selection, same-initialization refits and exact full-fit rail are implemented and synthetic-tested; close the gate only with *original-cache* numerical checks for normalization, initialization, selected steps, fitted directions and issued scores.
4. Reproduce at least the Table II/III/IV statistics from controlled publishable caches and resolve all peer-baseline licensing.
5. Source-based EPF download helper and executable package commands are present. Still require complete public-market processing/Host-cache generation and named as-of state manifest, dataset-specific licensing, GEFCom2014/DK1/NEM acquisition, and measured complete replay environment. A raw CSV download alone cannot reproduce a frozen Base forecast.
6. Run public-artifact scan (private paths, user names, credentials, patient/company records, proprietary price tables, checkpoints, images).
7. Obtain author approval for code licence and public visibility, then perform an audited commit/push/release on the *existing* repository only. Keep missing original forecast-cache and baseline reproducibility gates explicitly NOT READY unless evidence closes them.

**One original public DE.csv source file (52,416 hourly rows) was downloaded into gitignored `data/public/DE.csv` for local acquisition testing. It is not part of the Git publication candidate. No private Chinese records, Base caches or checkpoints were copied into the public package.**
