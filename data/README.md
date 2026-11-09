# Dataset interface (no redistributed data)

All datasets must be acquired from their respective official publishers and placed **outside this Git repository** or under an ignored local path.

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
