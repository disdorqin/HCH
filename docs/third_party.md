# Third-party sources and licensing

## Data

The five historical EPF Toolbox benchmark CSVs are hosted at https://zenodo.org/records/4624805 and accessed by the upstream project https://github.com/jeslago/epftoolbox . The upstream data readme documents original market sources and periods. The benchmark record is indicated as **other-open** by the EPF dataset-source reference, and the collectors do not claim ownership of all underlying feeds. Consequently, HCH does **not** redistribute these CSVs. Run `python scripts/fetch_epftoolbox.py --dataset DE` to download into an ignored local folder; check the source terms yourself.

For PJM source-level feeds, https://www.pjm.com/markets-and-operations/etools/data-miner-2/ explicitly restricts redistribution without active membership. Do not upload downloaded PJM raw feeds or model-cache derivatives to this repository. Other markets similarly require a source-by-source rights check.

## Forecasting models and postprocessors

The frozen upstream forecasting Base predictors are PatchTST, TimeMixer, iTransformer and LSTM. They are used as registered and are not bundled or retrained here. The comparison set includes PIR, delta-Adapter and UEC-STD; their upstream source, precise revisions and distribution permissions must be attached before their implementation is published as part of a complete benchmark reproduction. The HCH core does not import third-party baseline implementations.

## Reuse permissions

The source repository currently carries no author-approved open-source LICENSE file. Source availability does not grant permission to redistribute third-party data/code. See the author-facing publication checklist before changing the repository visibility or attaching a license.
