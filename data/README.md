# Dataset interface and source-attributed foreign data

A publisher-permitted, attributed Australia NEM SA1 hourly file is included under [data/foreign/NEM_SA1](foreign/NEM_SA1/README.md). Other market datasets must be obtained from original publishers, using the [foreign data availability matrix](foreign/README.md), or kept in ignored local directories unless the rightsholder grants explicit redistribution permission.

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
