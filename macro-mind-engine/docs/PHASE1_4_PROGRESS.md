# Phase 1.4 execution and resume log

Final status: READY_FOR_PHASE_1_5. G01–G39 PASS. Existing 207 + new 44 = 251 tests
passed; no failures/errors/skips. Phase 1.4 pending work: none. Phase 1.5 NOT_STARTED.
Latest authority: phase1/phase1_4_gate_result.json and phase1_4_evidence/run_002.
The following checkpoints preserve execution history, including earlier pending work.

Actual prompt: `codex迭代/codex prompt/20260928MacroMind Codex Phase 1.4 Legacy Compatibility Execution Prompt.md`.
The user supplied 20270928; the actual matching document is dated 20260928.
No Git repository exists. Do not recreate phase1_4_input_hashes.json or any earlier baseline.

Completed and verified:
- Read complete Prompt, inventory shape signatures and accepted finalization/hotfix records.
- Recorded 171 historical artifacts and the initial engine file hashes before adapter edits.
- Verified the Phase 1.3 manifest had no mismatches before the CLI extension.
- Existing tests rerun: 207 passed, 0 failed/error/skipped. Raw output and JUnit:
  phase1/phase1_4_existing_baseline.txt and .xml.
- Generated structural inventory and deterministic lineage. GS004 acceptance has
  completed finalization; GS005's original failed finalization remains historical,
  superseded by completed Hotfix 1.1 with an output-hash-linked completion record.
- Implemented compatibility runtime models, detector, registry, section adapters,
  stable identities, conservative mapping/loss/quarantine, Validator integration and CLI.
- Five runtime families include four actual legacy shape families plus canonical
  pass-through. Text-only includes documents other than Golden summaries; this is a
  safe raw-only carrier, not a claim of semantic coverage for every Markdown file.

Tests iteration 01: 38 passed, 1 failed (raw .txt and JUnit .xml retained).
The failed nullable test used Claim.statement, which the unchanged canonical schema
requires as nonempty Text. The adapter correctly quarantined those records. Corrected
the null/unknown/missing fixture to Claim.population, where all three are legal, and
added a separate assertion that unavailable Claim.statement must remain quarantined.
No test was removed and no schema or Validator rule was weakened.

Historical stage before acceptance: synthetic + targeted real compatibility verification, NOT ACCEPTED at that point.
Pending at that historical checkpoint (subsequently completed):
1. Rerun tests after fixture correction and complete mapping/raw-pointer checks.
2. Review real adapter losses and retained accepted decisions; no full Golden regression.
3. Finalize docs/matrix/policy, schema/registry gaps, conservative debt overlay.
4. Extend bounded verify_phase1_4.py with test/lint/CLI/immutability and G01–G39 checks.
5. Run final acceptance, retain every failed run, create source/artifact-hashed manifest.

Protected: Frozen/Golden, contract/schema/registry/validation code, registries/schemas,
all prior Phase 1.3 reports. Only compatibility, new tests, CLI extension, this phase's
script/docs/artifacts are allowed. No Phase 1.5/1.6, production or Skill work.

Checkpoint before bounded acceptance:
- Iteration 03: 42 new tests passed, including every real canonical leaf's mapping
  coverage and source/target value hashes across five targeted representatives.
- Required docs and bounded gate script implemented; final execution still pending.
- A script startup attempt failed before run directory creation: missing sys import
  after an earlier unused-import cleanup. Ruff's raw F821 output is retained in
  phase1/phase1_4_lint_iteration.txt; import restored. This was not a Gate pass.

Post-run_001 review:
- First bounded run passed 249 tests (207 existing + 42 new), all CLI/lint/hash/gate checks.
- Additional review identified explicit historical machine_use_policy exclusions that
  were preserved raw but also needed to stay outside active canonical occurrences.
  Added a generic policy-driven quarantine (no Golden/object id hardcoding), two
  regression tests and strengthened the actual GS005 accepted-decision test.
- A new acceptance run is required for these changes. Preserve run_001 as its original
  evidence; it does not certify the updated code until the next run completes.


Latest checkpoint: phase1/phase1_4_evidence/run_001
- Gate: READY_FOR_PHASE_1_5
- Existing tests: {'PASSED': 207, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}
- New tests: {'PASSED': 42, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}
- Pending: []
- Raw outputs and immutable run snapshots retained. Phase 1.5 NOT_STARTED.


Latest checkpoint: phase1/phase1_4_evidence/run_002
- Gate: READY_FOR_PHASE_1_5
- Existing tests: {'PASSED': 207, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}
- New tests: {'PASSED': 44, 'FAILED': 0, 'ERROR': 0, 'SKIPPED': 0}
- Pending: []
- Raw outputs and immutable run snapshots retained. Phase 1.5 NOT_STARTED.
