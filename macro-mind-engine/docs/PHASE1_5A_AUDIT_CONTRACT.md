# Phase 1.5A Audit Contract & Normalization

Audit version: **0.1.0**. This is a read-only engineering normalization contract, independent of Frozen Ontology V0.3, Schema 0.1.0 and Registry 0.1.0. It consumes existing results; it does not run or modify Validator, Compatibility, or Golden data.

## Explicit input and hash boundary

`AuditInputArtifact.from_file(path, artifact_type=..., phase=..., component=..., expected_sha256=...)` captures exactly the supplied file bytes once. SHA-256 is over those bytes. The captured JSON must still equal `content` at normalization time. No directory discovery or file writes occur in the runtime package. A captured artifact is a snapshot; subsequent external file changes require the caller to load a new snapshot. Acceptance separately rechecks the physical input files after normalization.

`from_content(...)` deep-copies an already parsed JSON value. Its hash is over UTF-8 canonical JSON with sorted keys, compact separators, finite numbers and one LF terminator. Raw-file hashes and canonical-value hashes have deliberately different, explicitly recorded `hash_basis` values. `expected_sha256`, when provided, is checked on capture and on every normalization. A mismatch, including nested content tampering, is a hard error. Every envelope in a bundle is verified before the first record is normalized; no partial result is returned.

`AuditInputBundle` has explicit groups for validation reports, adaptation results, immutability reports, gates, tests, schema/registry gaps, debt overlays and manifests. A group's envelope declares its actual `artifact_type`. Unknown types and unsupported shapes are retained, not inferred from a label, filename, or message. Input manifests are source inventories, not ontology registries.

## Supported source contracts

| Artifact type | Original collection | Audit record type |
|---|---|---|
| validation_report | issues | VALIDATION_FINDING |
| adaptation_result | losses | ADAPTATION_LOSS |
| adaptation_result | quarantined_items | QUARANTINE |
| adaptation_result | mapping_ledger | MAPPING_EVENT |
| adaptation_result | unknowns, warnings, unsupported_fields | UNKNOWN_ENGINEERING_RECORD |
| schema_gap_report | gaps and inherited_phase1_3_gaps | SCHEMA_GAP |
| registry_gap_report | gaps and inherited_phase1_3_gaps | REGISTRY_GAP |
| immutability_report | each original root field, including empty change arrays | IMMUTABILITY_EVENT |
| gate_result | gates and optional root status | GATE_RESULT |
| test_report | cases and the three Phase 1.4 count summaries | TEST_RESULT |
| debt_overlay | debts, sorted by recorded debt key | DEBT_STATUS |
| manifest or unsupported shape/type/format | whole original payload at the empty JSON Pointer | UNKNOWN_ENGINEERING_RECORD and unsupported_inputs |

These mappings are based on actual Phase 1.3 and Phase 1.4 artifacts. Validator's `errors`, `warnings` and other filtered views are not separately normalized because they repeat `issues`. Adaptation canonical objects and `raw_document` are not interpreted as engineering findings. An empty supported collection yields no invented finding. Empty immutability change arrays are retained as original observations, without manufacturing a PASS judgment.

`source_severity`, `severity` and `normalized_severity_class` retain the exact declared source severity; missing severity remains null. The display class introduces no ordering, score, or conversion. `source_outcome` independently preserves structured outcome/status/current_outcome, so a WARNING-severity INDETERMINATE result remains both. Gate FAIL/PASS and debt statuses are outcomes, not newly assigned severities. Loss, quarantine, gaps, warnings and debt remain different record types. Opaque unknown records preserve their entire payload without interpreting arbitrary keys as trusted severity fields. Unknown, null, empty arrays and false retain their original JSON types in `metadata.source_record`.

Messages are preserved text. The normalizer selects existing structured fields and never parses prose to invent a category. Every record includes the complete original source item under `metadata.source_record`; no unknown source fields are dropped from that item. Other report-level contextual fields remain in the hash-identified source artifact.

## Provenance and deterministic identity

Every source pointer follows RFC 6901, including escaping `/` and `~`. The empty pointer identifies a whole unsupported input. It resolves against the captured content and must equal the preserved source item. Record identity is `audit:` plus SHA-256 of the canonical tuple `[source_artifact_hash, source_pointer, record_type]`.

Artifacts are ordered by type/hash/id. Arrays retain source order; dictionary debt keys are sorted. Repeated equal items at different array pointers remain separate records, including 10,000 equal losses. Duplicate artifact envelopes and overlapping record identities are rejected explicitly, never silently deduplicated. The same envelope should be supplied once. Content-derived default artifact IDs avoid path-based identity.

`NormalizedAuditBundle.semantic_payload()` excludes envelope `path_or_label` and caller operational `source_metadata`. It includes records, verified content identities, supported/unsupported status and record counts. Its SHA-256 is `deterministic_hash`. No current clock, machine name or run ID is injected. Renaming identical source bytes preserves records and semantic output. Historical timestamps/paths already present inside immutable source bytes remain source evidence and are not scrubbed; changing them changes the source hash by design. Whitespace changes in a file also change its byte identity. This differs from renaming an unchanged file.

The normalization layer creates neither continuity annotations nor threads. Human-entered `ContinuityAnnotation` is a separate contract described in `ANALYTICAL_CONTINUITY_HOOK.md`.

## Reproducible verification and resumability

Run from the engineering root using the existing virtual environment:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/verify_phase1_5a.py
```

This script is a bounded acceptance check with nine explicitly listed historical inputs, not a production Audit Runner. It runs current pytest collection, warning-as-error, lint and formatting checks; checks every real record's provenance; validates Phase 1.4's existing manifest; compares protected file hashes; and evaluates A01–A25. Runtime import inspection permits only the used standard-library modules and Pydantic. No LLM, network, embedding or classifier dependency is present.

Lint uses an explicit configuration path and the same workspace-parent working directory as the recorded Phase 1.4 command. Ruff's implicit first-party import discovery depends on the working directory. Acceptance run 001 preserved 314 passing tests and all 25 passing gates but correctly returned NOT_READY because its lint command ran from the engine directory and disagreed with historical import grouping. The verification command was corrected; protected files were not reformatted.

Run 002 passed tests, lint and formatting but stopped at scope checking: an external Harness prompt appeared as `.hermes/macromind/1.md`, then was externally renamed to `.hermes/macromind/hermes_phase1_5a_pilot.md`. The user explicitly approved preserving and separately recording this concurrent file. `phase1_5a_external_workspace_observation.json` records that decision and the exact path/hash. Verification exempts only that matching new file from Phase 1.5A additions, not the directory or any protected changes. This file is not a Phase 1.5A implementation output, is not executed by this task, and is preserved unchanged.

`phase1/phase1_5a_input_hashes.json` preserves the pre-implementation protected baseline. `phase1_5a_evidence/baseline/` contains the actual 251-test baseline and Phase 1.4 verification (154 hashes, no mismatches). Each acceptance run uses a new numbered evidence directory with raw command streams, command arguments, JUnit, checks and manifest. Failed attempts are preserved. Development attempt 001 had 59 passes and one test-expectation failure: envelope construction correctly rejected a corrupted artifact before the test reached the Normalizer. The test now mutates a constructed bundle to exercise the normalizer's own preflight barrier.

Machine outputs include the input manifest, normalization report, test report, immutability report, gate result, manifest, progress JSON and append-only progress JSONL. The progress log describes work; it is not acceptance proof. Resume from its unfinished list and inspect current raw evidence and gate status. If verification is interrupted, the script records the exception and unfinished work when writable. An external termination may leave `acceptance_running`; inspect that evidence directory and run a new verification attempt instead of assuming completion.

Allowed changes are only the audit package/tests, this verification script, the two Phase 1.5A documents and `phase1/phase1_5a_*`. All existing engine files and historical Golden files are protected. No CLI, pattern aggregation, audit dashboard/report, runner, cross-run diff, Golden Regression, automatic repair, model or skill work is part of this phase. Phase 1.5B, 1.5C and 1.6 remain NOT_STARTED; Production, Analyst Model and Analyst Skill remain NOT_READY.

The latest gate-by-gate results below are generated from current evidence by the acceptance script.



<!-- ACCEPTANCE -->
## Latest acceptance evidence

Gate: `READY_FOR_PHASE_1_5B`. Evidence run: `phase1/phase1_5a_evidence/run_003`.

| Gate | Criterion | Result |
|---|---|---|
| A01 | Phase 1.4 final state still accepted | PASS |
| A02 | Existing tests all PASS | PASS |
| A03 | Supported artifacts normalize | PASS |
| A04 | Unsupported input preserved/reported | PASS |
| A05 | Source hashes verified | PASS |
| A06 | Every AuditRecord traceable | PASS |
| A07 | Deterministic record IDs | PASS |
| A08 | Deterministic output | PASS |
| A09 | Filename/path invariance | PASS |
| A10 | Severity preserved | PASS |
| A11 | Unknown/Indeterminate preserved | PASS |
| A12 | Source inputs unchanged | PASS |
| A13 | Frozen unchanged | PASS |
| A14 | Golden unchanged | PASS |
| A15 | Schema unchanged | PASS |
| A16 | Registry unchanged | PASS |
| A17 | Validator unchanged | PASS |
| A18 | Compatibility unchanged | PASS |
| A19 | Continuity defaults unreviewed | PASS |
| A20 | No automatic Thread creation | PASS |
| A21 | No LLM/network/NLP | PASS |
| A22 | Phase 1.5B NOT_STARTED | PASS |
| A23 | Phase 1.5C NOT_STARTED | PASS |
| A24 | Phase 1.6 NOT_STARTED | PASS |
| A25 | Analyst Model/Skills NOT_READY | PASS |

Existing tests: {'PASSED': 251, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}. New tests: {'PASSED': 63, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}.

26220 records from 9 inputs; 1 unsupported manifest retained explicitly.
