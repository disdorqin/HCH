# Foreign-market data availability

Files stored here are original-source-derived data **only when their publisher grants redistribution rights**. Data source availability and permission to republish the source file are not equivalent.

| Paper market | Dataset | Repository status | Reason / authorized alternative |
| --- | --- | --- | --- |
| Australia NEM South Australia | `NEM_SA1/SA1_2024_hourly.csv` | **Uploaded** (AEMO attributed data) | [Source/transform/licence](NEM_SA1/README.md) |
| Germany | EPF Toolbox DE | **Link / download, not redistributed** | [Zenodo dataset](https://zenodo.org/records/4624805), source rights marked other-open |
| PJM | EPF Toolbox PJM | **Link / download, not redistributed** | [Zenodo dataset](https://zenodo.org/records/4624805); [PJM redistribution restrictions](https://www.pjm.com/markets-and-operations/etools/data-miner-2) |
| GEFCom2014 | GEFCom2014 price track | **Not uploaded** | Public benchmark access exists, but explicit raw-series redistribution permission has not yet been established |
| Nord Pool NP | EPF Toolbox NP | **Link / download, not redistributed** | [Zenodo dataset](https://zenodo.org/records/4624805); [Nord Pool licensing](https://www.nordpoolgroup.com/en/services/power-market-data-services/faq/faq-premium-container/what-kind-of-redistribution-licences-do-you-have/) |
| Nord Pool DK1 | original DK1 2022–2024 data | **Not uploaded** | [Nord Pool redistribution licence](https://www.nordpoolgroup.com/en/services/power-market-data-services/faq/faq-premium-container/what-kind-of-redistribution-licences-do-you-have/) required |

The local paper-side inventory covers five Chinese development markets and six international datasets. This directory is **not** an issue-time-compliant HCH experimental cache: the Base forecasts, rolling residual histories, as-of-availability manifest and original chronological evaluation split are not included.

**Important:** `public=true` in the internal dataset registry indicates a publicly obtainable *source*, not a grant to republish that source. Do not copy the private Chinese markets, PJM / Nord Pool raw price records, EPF Toolbox CSVs or unauthorized checkpoint-derived caches into the Git repository.
