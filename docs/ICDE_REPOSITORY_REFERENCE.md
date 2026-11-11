# ICDE 2025 TimeKD → HCH: publication-repository functional audit

**Reviewed:** 2026-11-11. Live reference: [TimeKD](https://github.com/ChenxiLiu-HNU/TimeKD), the paper *Efficient Multivariate Time Series Forecasting via Calibrated Language Models with Privileged Knowledge Distillation* (ICDE 2025, pp. 3165–3178; [paper PDF](https://arxiv.org/pdf/2505.02138), [DOI](https://doi.org/10.1109/ICDE65448.2025.00237)). The paper's *Implementation Details* section links its source repository. HCH repository: [disdorqin/hch-forecast-repair](https://github.com/disdorqin/hch-forecast-repair).

## 1. Inspect the *actual* TimeKD repository (not a generic template)

GitHub's recursive source-tree read gives these functional groups:

| TimeKD actual files | Purpose (verified from files) | HCH equivalent | Assessment |
| --- | --- | --- | --- |
| `README.md` | Paper link/diagram, BibTeX, dependencies, external dataset URL, two execution commands, contact | `README.md`, `CITATION.cff` | **Local complete**; current GitHub README remains earlier scaffold with data-link amendment; pending synchronization |
| `data_provider/data_loader_emb.py`, `data_loader_save.py` | Split/window/scaling ETTh and Custom loaders; read/write stored teacher embeddings | `src/hch/data_loader.py`, `evidence.py`, `data/README.md` | **Partly equivalent:** an already-issued-cache schema exists; raw market → issue-time Base forecast/residual/state preparation does **not** |
| `model/TimeKD.py` | TimeKD's `Dual` student forecasting network | `src/hch/model.py` | **Corresponds by role, not architecture:** HCH is GRU32 post-forecast direction, not a trainable Base |
| `layers/{StandardNorm,Transformer_EncDec,SelfAttention_Family,Embed,Sub_CA,...}.py` | Transformer normalization, attention and embedding submodules | `src/hch/evidence.py`, `model.py`, `calibration.py` | **Corresponds by responsibilities**; no teacher attention / CLM layers needed in HCH |
| `clm.py` | Frozen GPT-2 teacher/prompt embedding branch | **No counterpart by design** | HCH has no language-model teacher or privileged-knowledge distillation |
| `utils/kd_loss.py`, `losses.py`, `similar_utils.py` | Feature/forecast/reconstruction/attention KD objectives | `src/hch/capacity.py`, `calibration.py`, `pipeline.py` | **Different science:** HCH fits direction and a nonnegative weighted-median distance |
| `utils/metrics.py`, `timefeatures.py`, `tools.py` | Forecast errors, time features, scaling/utilities | `src/hch/data_loader.py`, `evidence.py`, `scripts/hch_cli.py score` | Core metrics/time roles implemented; public real-market metric reproduction remains gated |
| `store_emb.py`, `Store.sh` | Precompute `*.h5` teacher embeddings, before running student training | **HCH needs a *different* preparation stage:** original Base issue-time caches | **Outstanding:** do not add dummy `Store.sh` or publish private Base caches |
| `train.py`, `Fcst.sh` | Student train and forecast, shell-loop hyperparameters | `src/hch/pipeline.py`, `scripts/hch_cli.py fit/predict/score` | **Local executable** (synthetic tests), no full real-market train/predict replay |
| `env_ts.yaml`, `env.txt` | Conda environment and package versions | `pyproject.toml` | **Adequate** for installable HCH core; no need to mirror TimeKD's exact CUDA packages |
| `LICENSE.txt` | S-Lab License 1.0, noncommercial terms | **No LICENSE yet** | **Author decision required**; do not copy TimeKD's licence or select a licence without approval |
| Data section of TimeKD README | Readers fetch datasets via external TimesNet link; no full raw data folder | `data/`, `scripts/fetch_epftoolbox.py`, `data/foreign/` | HCH's attributed AEMO NEM-SA1 CSV already exists on private remote; other sources are linked/licence-controlled |
| No equivalent test/CI tree in TimeKD root | Basic executable shell commands | `tests/`, `.github/workflows/ci.yml` | HCH local automated contracts **stronger for this aspect**; passing tests is not a paper-table reproduction claim |

**Important differences:** TimeKD's `Store.sh` writes cached privileged teacher embeddings; HCH's missing real-input preparation instead concerns **frozen Base issued forecasts plus already-revealed historical residual evidence and verified as-of fields**. These are NOT interchangeable. TimeKD's README uses a `/path/to/project_root` placeholder and its shell scripts fix the CUDA device (`cuda:7`); its data are primarily external. Its public repository is a helpful organizational reference, not proof that every paper code artifact must bundle every raw dataset.

## 2. HCH local final reader layout (existing files, no empty shells)

```text
hch-forecast-repair/
├── README.md                 # method, installation, sources, fit/predict/score, citation/contact
├── pyproject.toml            # installable Python package, CPU-capable dependencies
├── CITATION.cff              # four author-confirmed names; not yet on remote
├── configs/frozen_b2.yaml    # HCH registered settings
├── data/
│   ├── README.md             # target-free issued cache schema / temporal constraints
│   ├── china/README.md       # institutionally restricted data: no release
│   └── foreign/
│       ├── README.md         # six-foreign-market provenance/redistribution matrix
│       └── NEM_SA1/README.md # AEMO origin, transformation, attribution
├── src/hch/
│   ├── model.py              # seven-patch GRU32 direction model
│   ├── evidence.py           # 168-h historical evidence / masks
│   ├── calibration.py        # nonnegative lower weighted-median calibration
│   ├── capacity.py           # chronological capacity selections
│   ├── pipeline.py           # OOF fitting, frozen bundle, predict (LOCAL only)
│   └── data_loader.py        # time/role-restricted issued cache contract
├── scripts/
│   ├── hch_cli.py            # synthetic demo / fit / predict / separate score (LOCAL only)
│   ├── fetch_epftoolbox.py   # original Zenodo source fetch, no third-party redistribution
│   ├── replay_ablation.py    # existing 24-cell aggregate replay, not new training
│   ├── check_cache.py        # cache contract checker
│   └── release_audit.py      # candidate file/secret heuristic audit
├── examples/quickstart.py   # synthetic file-boundary fit→predict→score (LOCAL only)
├── tests/                   # source-matching and chronology/inference regressions
├── docs/
│   ├── reproduce.md         # exact commands, inputs and full replay limits
│   ├── third_party.md       # data/source provenance and licensing
│   ├── PROVENANCE.md        # frozen research-source hashes, gates
│   ├── ICDE_REPOSITORY_REFERENCE.md
│   └── supplement.pdf       # 8-page independent Supplement (LOCAL only)
└── .github/workflows/ci.yml # tests and publication candidate scan
```

The **remote** `main` separately contains `data/foreign/NEM_SA1/SA1_2024_hourly.csv` (8,786 rows; source-attributed AEMO) and explanatory Markdown. The CSV could not be copied into the local Git worktree through DevSpace due to HTTP 413; source and remote original Git blob were independently verified. The local tree above does **not** contain the CSV. Do not call the 33-local-file candidate a full manifest of the remote publication or force-push it.

## 3. Recorded acceptance gates and truthful status

| Acceptance criterion | Local candidate | GitHub current `main` |
| --- | --- | --- |
| Organized functional folders and reader-focused README | **PASS** | **PARTIAL**: earlier README and files; SA1 data links updated |
| Installable environment | **PASS** (`pyproject.toml`) | Early core pyproject available; latest package uncommitted |
| `fit → predict → score` demo with labels separated | **PASS**, synthetic 80 TRAIN / 5 later issue rows | **NOT UPLOADED**: `pipeline.py`, `hch_cli.py`, `examples/` still only local |
| HCH-S1-B2 alignment | **PARTIAL**: frozen forward & source-order synthetic tests | Early source-core only; original-cache numerical replay absent |
| Supplement | **PASS locally**, 8 pages, 598,838 bytes | **NOT UPLOADED** |
| Paper result replay | **PARTIAL**: Table III from existing aggregate CSV (requires authorized external input) | **NOT UPLOADED** as standalone workflow |
| Foreign datasets | SA1 source available in frozen research tree; DE original locally ignored | **PASS for SA1 only**. Five foreign sources remain download-/licence-gated |
| Citation / authors / licence | Four-author `CITATION.cff` exists; no author-approved licence | **No CITATION.cff / no LICENSE** |
| CI | 12 local pytest tests passed on 2026-11-11; source freeze test available locally | Hosted post-sync CI and anonymous access **NOT VERIFIED** |
| Reviewer-facing repository | Current local candidate can be presented privately | **Private**; anonymous reviewers cannot use it without provisioned access |

**Decision:** HCH's **functional folder decomposition aligns with TimeKD** and need not be rebuilt. Local candidate is a usable method demonstration. Full reproducibility of main 44-cell results remains a separate scientific-input gate because frozen four-Host predictions, exact processing/split manifests, as-of feature release records and some dataset licences have not been authorized/packaged.

**One-time repository closure:** obtain author approval for a private code sync and licence/public visibility decision; first reconcile remote SA1 data commits with local uncommitted work (remote `main` 6b704c6280db5c25fa20c6c2087ee42e4bb3fd1a; local HEAD 6387753bcb539392136df221701a9b86e252ad8d). No force push. Re-run tests, read back README/CLI/Supplement on GitHub and verify private or anonymous reviewer access accordingly. Keep real-market full-replay limitations in `docs/reproduce.md`, not repeated everywhere in the README.
