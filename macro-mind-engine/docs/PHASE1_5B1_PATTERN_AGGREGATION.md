# Phase 1.5B-1 Engineering Pattern Aggregation

Pattern version **0.1.0**. This phase adds `macromind.audit.patterns` without changing the accepted Phase 1.5A package files, tests, verifier, documents or machine artifacts. The layer consumes existing `AuditRecord` / `NormalizedAuditBundle` objects and emits structural indexes, not additional occurrences or ontology objects.

## Inputs and API

```python
from macromind.audit.models import NormalizedAuditBundle
from macromind.audit.patterns import PatternAggregator

bundle = NormalizedAuditBundle.model_validate_json(accepted_report_bytes)
result = PatternAggregator().aggregate(bundle)
```

`aggregate` also accepts an explicit list of Phase 1.5A AuditRecord instances. It does not load files, scan directories, invoke the Normalizer, construct AuditRecords, or access the network. Bundle input must match its recorded type counts and semantic hash. Invalid identities, duplicate record IDs, damaged structural fields and inconsistent indexes produce hard errors; the API never returns partial aggregation.

The formal acceptance input is exactly `phase1/phase1_5a_normalization_report.json`, checked against the pre-implementation SHA-256 baseline and the Phase 1.5A accepted manifest. It is not regenerated. Baseline collection contains 314 passing tests, but acceptance compares actual collected test identities rather than relying on that number alone.

## Disposition contract

| Disposition | Record types |
|---|---|
| PATTERN_ELIGIBLE | VALIDATION_FINDING, ADAPTATION_LOSS, QUARANTINE, SCHEMA_GAP, REGISTRY_GAP |
| TRACE_ONLY | MAPPING_EVENT |
| SUMMARY_ONLY | TEST_RESULT, GATE_RESULT, IMMUTABILITY_EVENT, DEBT_STATUS |
| OPAQUE_EXCLUDED | UNKNOWN_ENGINEERING_RECORD |

Each input record has exactly one disposition. Only eligible records reach signature construction. Opaque payloads are never interpreted for grouping; the output retains their disposition, count and unique source-artifact count. Mapping trace events and engineering summaries cannot create issue patterns, regardless of their volume. Eligibility depends solely on record type, not severity, outcome or message; a Validator PASS occurrence therefore remains eligible under this exact first-version policy.

## Signature and paths

A PatternSignature consists exactly of record_type, component, category, rule_id, reason_code, structured_dimensions, source_path_shape and target_path_shape. Missing optional scalar fields remain null. Missing dimensions are not invented.

The dimensions whitelist is source_family, source_object_type, target_object_type, object_type, field, field_name, source_field and target_field. AuditRecord 0.1.0 has no such top-level fields, so this implementation reads only explicitly present keys in `metadata.source_record`. It never reads message prose, descriptions, review notes, filenames, directories, source IDs, hashes, source-pointer indexes, timestamps, thread labels or operational metadata to infer a dimension. A missing or non-object source snapshot contributes no dimensions while preserving the occurrence and top-level signature.

Declared dimension values support finite JSON scalars, including an explicit null. Nested objects/arrays in a declared dimension are rejected rather than allowing opaque prose to enter the signature. The accepted real eligible records contain only string dimension values (source_family and source_object_type), so this conservative contract is not a blocking design gap for the current input. Future structured dimension extensions require a separately reviewed contract; no fuzzy fallback is supplied.

Paths are null or RFC 6901 JSON Pointers. The empty string remains the root pointer. Only complete canonical ASCII array-index tokens (`0` or a nonzero digit followed by digits) become `*`. For example, `/claims/12/source_refs/2` becomes `/claims/*/source_refs/*`. Escaped field names, mixed tokens, signed numbers, leading-zero tokens and non-ASCII digits are preserved. Malformed pointer syntax raises an error. No attempt is made to infer a business ID. With no original container context, canonical numeric pointer tokens follow the declared index-shape convention; a future need to distinguish numeric object keys requires explicit context, not guessing.

Pattern IDs are `pattern:` plus SHA-256 of the canonical signature. Severity and source_outcome do not split a signature. Different reason codes, rule IDs, record types, field names or retained dimensions do split it. Message changes, different source-artifact identities and numeric index changes do not split it.

## Statistics and complete drill-down

Every pattern stores all occurrence_record_ids, unique source_artifact_ids, exact counts, source severity/outcome distributions and the count of occurrences whose review_required is literally true. All identifiers and distribution keys are stably sorted. Examples are the first at most five sorted occurrence IDs; they never replace the full occurrence list.

Severity/outcome distribution keys preserve ordinary source strings such as ERROR and WARNING. JSON null uses `null`. To avoid colliding with a literal source string `"null"`, reserved strings are escaped as `str:` plus their JSON representation. Non-string outcomes use `json:` plus canonical JSON. Strings starting with `str:` or `json:` are likewise escaped. Thus false, `"false"`, null and `"null"` remain distinct. There is no severity ranking, priority, risk score or outcome conversion.

`pattern_occurrence_index.by_pattern` maps every pattern to its complete occurrences; `by_record` maps each eligible record to exactly one pattern. `validate_conservation` rejects missing occurrences, duplicate assignments, extra ineligible assignments, disposition/count mismatches and inconsistent forward/reverse indexes. The acceptance checks independently resolve every occurrence ID to the original input records.

Occurrence count is descriptive. It cannot automatically set review_required, create a debt, recommend repair, or propose changes to schema/registry/ontology. The largest pattern count is reported without calling it the most important or highest-risk pattern.

## Determinism and read-only behavior

`PatternAggregationResult.semantic_bytes()` is UTF-8 canonical JSON with sorted keys and one LF terminator. Its SHA-256 is deterministic_hash. Output patterns are sorted by pattern_id; input order does not affect grouping, indexes, statistics or semantic bytes.

The result retains input_normalization_hash as provenance. Phase 1.5A's bundle hash depends on record-array order; this provenance value is therefore explicitly excluded from the pattern result's semantic projection. A reordered bundle must have a valid recomputed Phase 1.5A hash, but its aggregation semantic output remains identical. No filename, current time, machine name or run directory is injected into the projection. Pattern identities exclude occurrence/source identities; complete occurrence indexes necessarily retain the accepted record IDs for reversibility.

Aggregation does not mutate the input bundle, its record objects or their nested data. Tests check original object identities and contents, reject an attempted constructor call for new AuditRecords, and verify accepted input bytes before and after real aggregation. Runtime code neither imports nor consumes ContinuityAnnotation. No AnalyticalThread, AnalyticalEpisode, Evidence Delta, Judgment Delta or SAME_ISSUE judgment is produced.

## Acceptance, scope and resume

Run the existing virtual-environment Python against `scripts/verify_phase1_5b1.py`. This is a bounded engineering verification script, not an Audit Runner or product CLI. It uses the recorded workspace-parent Ruff working directory and explicit configuration path so historical files are not reformatted to satisfy a changed import-discovery context.

The script verifies Phase 1.5A's accepted manifest, reruns all tests with warnings as errors, runs lint and formatting checks, reads the accepted report, performs three real aggregations and a record-order permutation, checks both index directions and counts, verifies source/protected hashes, and evaluates B101–B133. Counts are computed from actual record_counts and reconciled with actual records. No target pattern count is hardcoded.

Allowed changes are only the new patterns subpackage, tests/audit_patterns, this phase's verification script and document, and phase1/phase1_5b1_*. The 688-file starting baseline includes previous implementation/artifacts, Golden/Frozen sources, and the current external `.hermes` files. `.hermes` is read-only for this task. A later external change is recorded with its exact path/hash; the verifier stops for user confirmation rather than whitelisting the directory or inheriting another phase's exception.

Each run gets a new evidence directory with exact command arguments, raw stdout/stderr, JUnit, real checks, scope checks and artifact snapshots. Previous runs remain unchanged. Root machine artifacts are the current view; numbered runs preserve historical evidence. `phase1_5b1_execution_progress.json` and the append-only JSONL are resume aids, not acceptance authority. On interruption, use the recorded unfinished list plus raw evidence. Do not regenerate an already accepted input or overwrite a previous run.

The generated pattern_catalog contains full patterns and accepted input hash; pattern_occurrence_index contains both directions and integrity checks; disposition_summary contains every record disposition plus requested counts; aggregation_result retains the full typed result for independent semantic verification. Test, immutability, gate and manifest outputs record the current acceptance. Manifests hash generated files excluding themselves and snapshot manifests to avoid self-reference.

No Human Audit Report, Dashboard, Top Risks, Remediation Plan, continuity/thread indexes, Golden Regression, product CLI, model or skill artifacts are generated. Phase 1.5B-2, 1.5C and 1.6 remain NOT_STARTED; Analyst Model, Analyst Skill and Production remain NOT_READY.


<!-- ACCEPTANCE -->
## Latest acceptance

Gate: `READY_FOR_PHASE_1_5B_2`. Evidence: `phase1/phase1_5b1_evidence/run_002`.

| Gate | Criterion | Result |
|---|---|---|
| B101 | Phase 1.5A remains accepted | PASS |
| B102 | Existing tests all PASS | PASS |
| B103 | New pattern tests all PASS | PASS |
| B104 | Every AuditRecord has exactly one disposition | PASS |
| B105 | Eligible record types exact | PASS |
| B106 | Trace-only records excluded | PASS |
| B107 | Summary-only records excluded | PASS |
| B108 | Opaque records not semantically interpreted | PASS |
| B109 | Pattern signature structural only | PASS |
| B110 | Message metamorphism invariant | PASS |
| B111 | Numeric path-index metamorphism invariant | PASS |
| B112 | Different reason_code separates patterns | PASS |
| B113 | Different rule_id separates patterns | PASS |
| B114 | Different record_type separates patterns | PASS |
| B115 | Severity does not split structural pattern | PASS |
| B116 | Outcome does not split structural pattern | PASS |
| B117 | Eligible occurrence count conserved | PASS |
| B118 | Every eligible occurrence assigned exactly once | PASS |
| B119 | Bidirectional index consistent | PASS |
| B120 | Pattern IDs deterministic | PASS |
| B121 | Pattern output deterministic | PASS |
| B122 | Input order invariant | PASS |
| B123 | NormalizedAuditBundle unchanged | PASS |
| B124 | No new AuditRecords created | PASS |
| B125 | No Pattern to Debt promotion | PASS |
| B126 | No LLM/network/NLP/fuzzy clustering | PASS |
| B127 | Phase 1.5A existing source unchanged | PASS |
| B128 | Continuity Hook unchanged | PASS |
| B129 | Frozen/Golden/Schema/Registry/Validator/Compatibility unchanged | PASS |
| B130 | Phase 1.5B-2 NOT_STARTED | PASS |
| B131 | Phase 1.5C NOT_STARTED | PASS |
| B132 | Phase 1.6 NOT_STARTED | PASS |
| B133 | Analyst Model/Skill NOT_READY | PASS |

Real statistics (descriptive only):

```json
{
  "eligible_records": 7311,
  "largest_pattern_occurrence_count": 131,
  "opaque_excluded_records": 9499,
  "pattern_count": 281,
  "patterns_by_record_type": {
    "ADAPTATION_LOSS": 203,
    "QUARANTINE": 9,
    "REGISTRY_GAP": 8,
    "SCHEMA_GAP": 24,
    "VALIDATION_FINDING": 37
  },
  "summary_only_records": 308,
  "total_records": 26220,
  "trace_only_records": 9102
}
```

Existing tests: {'PASSED': 314, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}. New tests: {'PASSED': 80, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}.
