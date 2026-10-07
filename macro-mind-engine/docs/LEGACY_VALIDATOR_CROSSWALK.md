# Legacy validator crosswalk

Read-only sources: `../golden_sample_test/validate_gs004_ma1.py` and
`../golden_sample_test/migrate_gs005_ma1.py`. Neither is run by Phase 1.3.
This maps generic semantics, not a promise of identical behavior for legacy shapes.
The current canonical schema, reference contracts and frozen principles govern.

| Legacy | Classification | Current coverage and limits |
|---|---|---|
| R056 | ported_to | V-AN001/002: match evidence shape and eligible historical support; no hard recurrence count |
| R057 | ported_to; deferred; sample_specific | V-AN001: prior/scope/evidence presence; free-text specificity judgment deferred, hardcoded phrases and MR ids not ported |
| R058 | covered_by_schema; ported_to | V-SCH002, V-AN004 and V-ARG005 preserve observer/reasoner roles; no hardcoded analyst id or requirement that identity strings differ |
| R059 | covered_by_schema; deferred | V-SCH002 rejects validated_skill as Heuristic status; V-GOV003 records absent promotion evidence structure; no Skill compiler |
| R060 | covered_by_schema | V-SCH002: all six ComparisonBasis fields and legal comparison enum; V-BND006 preserves unknowns |
| R061 | ported_to; deferred | V-BND006 flags unclear percentage-point units; controlled dimensional conversion remains a gap |
| R062 | covered_by_schema; sample_specific | V-SCH002 legal role enum; audited sample-specific corrections and C005 exemption not ported |
| R063 | deferred | V-ARG006 records absent typed role/stage transition evidence; no rule that enum order is causal order |
| V-MA101 | covered_by_schema | V-SCH002 required canonical AnalystMethodSignal fields and enums |
| V-MA102 | ported_to | V-AN001, V-REF003/004/005 resolve active priors; uncertain+first_observation remains legal |
| V-MA103 | ported_to; deferred | V-AN001 requires recorded matched_scope for exact/partial/analogous; no NLP proof of specificity |
| V-MA104 | ported_to | V-AN004 records observed_reasoner_id independently; no analyst-specific constant |
| V-MA105 | ported_to | V-AN004 records annotation_observer; unknown attribution remains indeterminate |
| V-MA106 | covered_by_schema | V-SCH002 and V-GOV001: no Review exemption for ComparisonBasis shape |
| V-MA107 | ported_to; deferred | V-BND006 unit preservation and warning; no percentage/point conversion or unsupported dimensional inference |
| V-MA108 | covered_by_schema; sample_specific | V-SCH002 stage enum; C005/open-review exemptions not ported |
| V-MA109 | deferred | V-ARG006 typed transition gap; current schema cannot prove role conversion validity |
| V-MA110 | ported_to; deferred; sample_specific | V-AN003 explicit expression/context guards; mixed Argument scope requires review; SS-M prefixes/DA01 constants not ported |
| V-MA111 | ported_to; sample_specific | V-TEMP003 generic future-prior chronology using structured content times/cutoff; no GS ordinal chronology or sample exemption |

No C005, GS004-specific, open-review or resolved-review exemptions enter the engine.
No legacy field adapter is included. D03/D04/D11/D16/D20 remain partially addressed;
legacy records and full Golden regression are later-phase work.
