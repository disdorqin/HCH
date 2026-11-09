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

`src/hch/model.py` matches the frozen class constructor, feature segmentation and forward path. `calibration.py` reproduces the frozen nonnegative lower weighted-median convention. Unit tests cover controlled numeric equivalence against the frozen runner (when accessible). The public cache schema and timestamp/role checks are not yet proven end-to-end.

## Mandatory release gates

1. All frozen SHA checks PASS; no methodology changes in the original research checkout.
2. Test the clean core against original frozen outputs on matched, source-permitted forecast caches, not on invented market data.
3. Implement and audit chronological B0--B4 fitting, inner-tail selection, deterministic reset/refit and exact full-fit checkpoint rules.
4. Reproduce at least the Table II/III/IV statistics from controlled publishable caches and resolve all peer-baseline licensing.
5. Add actual data acquisition/download instructions, split manifests, disclosed dataset usage rights, measured runtime environment and actual commands.
6. Run public-artifact scan (private paths, user names, credentials, patient/company records, proprietary price tables, checkpoints, images).
7. Obtain author approval of license and availability of complete artifacts. Only then create/push a public GitHub repository.

**No raw datasets, checkpoints, or private market state have been copied by this project.**
