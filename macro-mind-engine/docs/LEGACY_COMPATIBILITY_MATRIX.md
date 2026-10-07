# Legacy compatibility matrix

| Family | Detection | Adapter | Loss profile | Target | Validator compatibility | Limitations | Representative |
|---|---|---|---|---|---|---|---|
| SUMMARY_ONLY_LEGACY | EXACT marker + shape or STRONG unique shape | compat.summary_only_legacy | PARTIAL: raw summary only; reconstruction forbidden | 0.1.0 | Canonical transport accepted; semantic errors retained | Partial bundles; no full Golden regression | golden_sample_test/golden_report.md |
| LEGACY_PRE_MA | EXACT marker + shape or STRONG unique shape | compat.legacy_pre_ma | PARTIAL/LOSSY_BUT_SAFE: missing semantics unknown or quarantined | 0.1.0 | Canonical transport accepted; semantic errors retained | Partial bundles; no full Golden regression | golden_sample_test/golden_sample_002/golden_sample_002.json |
| V0_3_LEGACY | EXACT marker + shape or STRONG unique shape | compat.v0_3_legacy | PARTIAL/LOSSY_BUT_SAFE: explicit fields only | 0.1.0 | Canonical transport accepted; semantic errors retained | Partial bundles; no full Golden regression | golden_sample_test/golden_sample_003/golden_sample_003.json |
| MA1_COMPAT | EXACT marker + shape or STRONG unique shape | compat.ma1_compat | Lossless only if every semantic field is representable; accepted history retained | 0.1.0 | Canonical transport accepted; semantic errors retained | Partial bundles; no full Golden regression | golden_sample_test/golden_sample_004/golden_sample_004.ma1_accepted.json; golden_sample_test/golden_sample_005/golden_sample_005.ma1_accepted.json |
| CANONICAL_0_1 | EXACT marker + shape or STRONG unique shape | compat.canonical_0_1 | Canonical pass-through; unsupported shapes quarantined | 0.1.0 | Canonical transport accepted; semantic errors retained | Partial bundles; no full Golden regression | Canonical synthetic fixture; not a real legacy family |

UNKNOWN_LEGACY and AMBIGUOUS have no selected adapter and return UNSUPPORTED.
Inventory has 171 files, including reports/scripts/text carriers; this does not mean 171 complete Golden datasets.
Canonical pass-through is excluded from the four observed legacy family count.
All five real representatives retain raw history, mapping/loss records and exact accepted decisions.
Detailed current counts and quarantine limitations: phase1/phase1_4_adaptation_summary.json.
