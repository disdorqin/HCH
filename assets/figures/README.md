# README figure provenance

These images are **rendered/copied from the manuscript's existing figures**. They are not newly simulated data, redesigned methods, or independent experiment results.

| README image | Paper source | Operation | SHA-256 of README image |
| --- | --- | --- | --- |
| `hch_overview.png` (2056 × 1160) | `paper/final_paper/main.tex` current `\\FIGFRAMEWORK` → `paper/assets/figures/fig02_overview/candidate_v9_visio_publication_repair_20261016/HCH_fig02_R53_author_review.pdf` | Page 1, 4× resolution, RGB PyMuPDF rasterization from publication PDF | `1083617d2d91dd9bfc0ce185eb46dc03ce1f02501142003547c0cba30d82572b` |
| `price_regimes.png` (2343 × 847) | `paper/final_paper/hch_r70_results.tex` Fig. *targeted_regime* → `paper/assets/figures/fig09_targeted_regime_repair/regime_three_panel_r49_palette_author_preview.png` | Byte-identical copy of existing publication figure | `96c5307e754eb5003ae17b7153f5c678c81c9f4bc11e23b4158d10ae0813f1dc` |

The original framework PDF SHA-256 is `2ff51ff9e18dd7b815d9aba3f4af4ec0a6db9056b73e4c2064c6ec4c679a4805`; the reviewed results TeX SHA-256 is `988cc242b05cb7152c5d04848406b0b174a87be1a775da267fd3f0b6fb81157b`.

The README normalized MAE numbers (Base = 100, Chinese development 91.19, additional development 90.97, confirmation 95.55, all 44 settings 91.90) are transcribed from the current `hch_r70_results.tex` Parameter Sensitivity and Efficiency paragraph / Table IV. The price-regime image corresponds to the registered three-panel development evaluation (negative price hours, large zero crossings, and upper-price tails).

**Release boundary:** this record documents source/figure identity, not transfer of third-party datasets or inclusion of private evaluation targets. The two README images and the changed README are presently **local Git candidates**, not yet present in the private GitHub remote; do not advertise their links as public until a coordinated approved synchronization has completed.
