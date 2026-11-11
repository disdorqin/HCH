# Dataset interface and foreign market data

An author-transformed, AEMO-attributed NEM South Australia hourly 2024 CSV has been uploaded to the existing GitHub repository: [data/foreign/NEM_SA1](foreign/NEM_SA1/README.md). Other foreign datasets require source-level reuse rights; see [the market-by-market status](foreign/README.md). Non-redistributable observations stay under ignored local paths or are fetched by readers from original publishers.

Expected forecast-repair cache fields (format contract; not fake sample data):

| Field | Shape | Meaning |
| --- | --- | --- |
| `issued_forecast` | `[N,24]` | Stored Base prediction generated at the origin |
| `history_price` | `[N,168]` | Historical observations already revealed at issuance |
| `history_residual` | `[N,168]` | Same-Base historical prediction residuals, NaN where unavailable |
| `residual_available` | `[N,168]` | Revealed residual availability mask |
| `future_state` | `[N,24,C]` | Forecast-known external-state channels, never realized target-day price |
| `origin_time` | `[N]` | Forecast issue/target-day time labels |
| `market`, `base_id`, `split` | metadata | Required matching and chronology identity |

**Source role:** Chinese province and commercial dataset rights have to be reviewed individually. Shandong is private/non-primary in the source registry. Public datasets may be linked with scripts but not redistributed without license review.

**Temporal guarantee:** Any external feature must be documented as publishable before the issue-time cutoff. A filename or target timestamp alone is insufficient provenance. This code does not claim a certified point-in-time feature store.
