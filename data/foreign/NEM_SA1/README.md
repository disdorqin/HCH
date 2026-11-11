# Australian NEM South Australia (SA1) — published 2024 hourly data

**File:** [SA1_2024_hourly.csv](SA1_2024_hourly.csv)

- Market: National Electricity Market, South Australia region (`SA1`)
- Origin: Australian Energy Market Operator (AEMO) public regional market price and demand records
- Official source: [AEMO — Dispatch / Trading data](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data/dispatch) and [AEMO market data](https://visualisations.aemo.com.au/aemo/nemweb/)
- Rights: [AEMO Copyright Permissions](https://www.aemo.com.au/privacy-and-legal-notices/copyright-permissions) grant general permission to use publicly available AEMO material with appropriate acknowledgement, subject to exceptions for confidential or externally owned material
- Attribution: **Source data © Australian Energy Market Operator (AEMO); hourly research transformation by HCH authors.** No endorsement by AEMO is implied.
- Source-format provenance: 2024 monthly public regional `SA1_YYYYMM.csv` records containing `REGION, SETTLEMENTDATE, TOTALDEMAND, RRP, PERIODTYPE`; this file is the registered hourly modeling product, not an unmodified AEMO export
- Hourly schema: `timestamp,price,TOTALDEMAND`
- Source file role: native regional reference price and **realized** total demand; includes 8,786 hourly rows spanning the 2024 interval and its terminal boundary timestamp at 2025-01-01 00:00
- HCH benchmark role: Australia NEM SA1 independent confirmation setting; the paper's scored eligible-origin count is **not** this file's row count

## Information-availability caution

`price` is an observed historical market result and `TOTALDEMAND` is **realized** regional demand. Neither column may be presented as a known target-day input at the forecast issue cutoff; the HCH experiment's forecast-known external-state channel count for NEM-SA1 is zero. This source CSV alone is not a train/test-split manifest or a reproducible issued prediction cache.

## Exact source identity

- Original local source checkout: `data/AEMO_NEM/NEM_SA1/processed/SA1_2024_hourly.csv` (source-research repository, unchanged)
- Original raw CSV byte size: **470,817** (CRLF)
- SHA-256 of original raw CSV bytes: `06e0fb851a4ae6a6e752a71fada9ca79cfbb2e5846e9fbdc44363ed790d9e20f`
- GitHub blob SHA of uploaded CSV: `468742b174683efe1ccdcda2b03f507e27768543` (exact raw bytes, independently matched to original)
- No model weights, private market observations, or future-realized labels from a protected forecast split are embedded.
