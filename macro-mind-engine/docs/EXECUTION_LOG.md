# Phase execution record

## Phase 1.0 — completed

Frozen contract loader and fail-closed tests implemented. The successful saved
`phase1/contract-tests.xml` records 21 passed, 0 failed, 0 errors, 0 skipped.
The initial attempt also passed test cases but failed writing JUnit XML because of
the execution environment's directory permissions; rerunning from the workspace
root with absolute paths produced the successful report. No contract was repaired.
Next: executable schema mapping, only after this gate passed.

## Phase 1.1 — completed

14 Core and 12 Auxiliary models; 26 JSON Schemas and field mapping exported.
`phase1/schema-tests.xml` records 38 passed, 0 failed, 0 errors, 0 skipped.
That run emitted one Pydantic instance-level model_fields deprecation warning;
the test now reads class-level model_fields. This does not change schema semantics.
Next: formal registry integrity and CLI integration.

## Resume inventory and Phase 1.2 verification

At the user's continuation request the workspace was inventoried without rebuilding
completed content. There is no `.git` repository in the workspace, so the cited
56-file change list cannot be reconstructed as a Git diff. The current engine has
89 non-cache/non-venv source/artifact files including generated schemas and reports.
All 171 original files covered by `phase1/input_hashes.json` remain byte-identical.

The original `registry-cli-tests.xml` and fresh `registry-cli-resume-tests.xml` both
record 24 passed, 0 failed, 0 errors, 0 skipped. These cover duplicate/unknown enums,
relation endpoints, replacements, schema versions, Core membership, automatic-merge
rejection, stale generated artifacts, duplicate YAML keys, missing files, unsafe
YAML tags, CLI success/error codes, structured logs and protected export paths.

Next: resolve static-check findings (imports and Typer annotation style), verify
installed entry point, write conservative debt overlay and reproducible final gate
reports. Phase 1.3, Batch Pilot, mining and Skills remain not started.

## Installed CLI check — generated formatting drift found

Editable package installation succeeded. Installed `contract verify` returned 0.
Installed `registry verify` returned 1 because the formatter had reformatted the
generated enum file despite the original path-specific exclusion. Vocabulary values
were unchanged; the byte-drift guard correctly rejected the artifact. The initial
failure is preserved in `phase1/installed_cli_report.json`. The formatter exclusion
was corrected to `**/_enums.py`, and only that derived file was regenerated from its
existing YAML authority. Final installed-entry verification is recorded separately.

## Final integration follow-up — Windows output encoding

The first full engineering gate passed 83 tests with warnings treated as errors.
Installed contract and registry commands then succeeded, but the external smoke-test
reader exposed a Windows code-page mismatch when the schema-export log contained a
temporary path with Chinese characters. CLI JSON now uses lossless ASCII escapes,
so both stdout and stderr are parseable independent of the console code page.
A subprocess regression forces GBK output with a Chinese registry path. This is a
logging fix only; schema and ontology content are unchanged.

## Phase 1.2 — completed

Final registry tests: 19 passed; CLI integration tests: 6 passed. Both groups have
0 errors, 0 failures and 0 skips. Object/enum/relation/version/identity registries
load successfully with exactly 14 Core entries. Enum generation and registry
roundtrips are deterministic. The installed `contract verify`, `registry verify`
and `schema export` entry points each returned 0; their outputs and structured
logs are retained in `phase1/installed_cli_after_fix_report.json`.

Next: final Phase 1.0–1.2 acceptance record.

## Final Gate — READY_FOR_PHASE_1_3

G01–G18 all PASS. Final tests: contract 21, schema 38, registry 19, CLI 6;
total 84 passed, 0 failed, 0 errors, 0 skipped, with warnings treated as errors.
Ruff passes. Contract integrity: 44 PASS, 0 ERROR, 0 WARNING. All 171 protected
files retain their original bytes and membership. 14 Core models, 12 Auxiliary
models and 26 exported JSON Schemas are present. Generated schemas and enums
match their sources; mapping documentation is current.

Machine results: phase1/gate_result.json, phase1/test_report.json,
phase1/phase1_0_1_2_manifest.json, phase1/immutability_report.json and
phase1/debt_status_overlay.json. D02/D07/D16/D18 remain partially addressed.

Next: MacroMind Codex Phase 1.3 Validator Engine under a subsequent execution
request. Phase 1.3 and Batch Pilot remain NOT_STARTED. Analyst Model, Analyst Skill,
MacroMind Core Skill and Production remain NOT_READY; production_import_ready=false.
