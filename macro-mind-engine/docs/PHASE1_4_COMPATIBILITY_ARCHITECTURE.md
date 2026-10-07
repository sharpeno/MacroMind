# Phase 1.4 compatibility architecture

The dependency direction is historical input → compatibility → canonical runtime
view → unchanged Phase 1.3 Validator. No legacy code enters the Validator.

## Inventory and authority

The bounded acceptance script inventories every existing historical file, recording
byte hashes, top-level shape, version fields, sections and field signatures. No Claim
meaning is evaluated. All 171 files are inventoried; README/report text is a safe
text-only carrier, not evidence of full Golden reconstruction coverage. Unknown
reports, scripts and unrelated shapes remain explicitly outside adapter selection.

Lineage records use migration/finalization metadata and matching output/input hashes.
GS005's failed first finalization remains recorded; completed Hotfix 1.1 supersedes it
without changing the original human decisions. Representative accepted inputs must
have acceptance metadata AND a hash-linked completion record. Filename and mtime do
not determine authority. Only five targeted representatives are adapted for acceptance:
actual summary, pre-MA, V0.3, and both accepted MA.1 artifacts. This is not a full
Golden semantic regression and does not establish expected historical truth verdicts.

## Runtime components

`detect_legacy_format(document)` accepts decoded data, not a path. EXACT requires a
recognized marker and corresponding shape; STRONG uses unique structural signatures.
The MA.1 signature refines its V0.3 parent; a simultaneous independent pre-MA envelope
is ambiguous. AMBIGUOUS/UNKNOWN never triggers adapter guessing. shape_hash uses
structural types/keys, not content classification or probability scores.

`CompatibilityAdapterRegistry` selects by detected family and target schema only.
Four legacy shape adapters share explicit numbered-section mappings; canonical
pass-through is an additional runtime adapter, not a newly invented legacy family.
`CompatibilityEngine.detect/adapt/adapt_file` expose the API. AdaptationResult contains
canonical_bundle, complete raw_document, quarantine, mapping/loss/unknown ledgers,
status, validation summary and an adaptation manifest. These are runtime structures,
not ontology types or exported schemas.

Stable unique ids are retained. Cross-type collisions are content-namespaced and refs
are mapped only after all ids have been allocated. Target contracts filter candidates;
ambiguous/missing/quarantined targets are never guessed. Indistinguishable duplicate
identities are quarantined. Anonymous ids hash object content and declared type, not
file path, clock or uuid. JSON section pointers remain in the mapping ledger.

Canonical dictionaries are built field-by-field through the unchanged model shapes.
Explicit aliases (claim_id → id, claimant_id → claimant when no canonical claimant,
from_claim → a one-element premise list) change representation only. Unknown
semantics are never derived from chapter names, financial context or sample numbers.
Scalars/nested values that cannot be safely represented are preserved with loss or
quarantined. Quarantine is an expected conservative compatibility result, not a claim
that a historical human decision was wrong.

## Determinism and preservation

Adaptation uses isolated snapshots. Source bytes are hashed before and after file
adaptation. Full inputs, unsupported fields and accepted decisions stay retrievable.
MappingEntry targets use `/canonical_bundle/...`, `/raw_document/...` and
`/quarantined_items/...`; every canonical leaf has source/default evidence. Value
hashes and mapping coverage are checked against all five real representative outputs.

Machine artifacts use sorted-key UTF-8 JSON with normalized newlines. Adaptation
semantic hashes exclude operational filenames, absolute input/output paths and clocks.
Historical path/timestamp strings already inside the source are preserved as source
content; they are not invented operational metadata. Renaming or relocating identical
bytes gives identical detection, ids, canonical bytes and adaptation hashes.

Reordering unordered top-level object arrays preserves the sorted canonical bundle
and its hash. Exact source byte hash, JSON pointers, raw_document and loss/mapping
ledgers necessarily reflect that changed input; the full adaptation hash is therefore
not required to remain equal under permutation. Ordered nested data (Argument steps,
branch lists, source cues and original reference lists) preserve recorded positions.

## CLI and output

```powershell
macromind compatibility detect --input legacy.json
macromind compatibility adapt --input legacy.json --output new_view.json --contract-root ../golden_sample_test/core_ontology/v0.3 --registry-root registries/v0_3
```

Detect returns 0 for EXACT/STRONG, 1 for AMBIGUOUS/UNKNOWN and 2 for input errors.
Adapt returns 0 for LOSSLESS/LOSSY_BUT_SAFE/PARTIAL, 1 for UNSUPPORTED and 2 for
usage/IO/malformed input. There is no --in-place. Output is AdaptationResult JSON;
its canonical_bundle is the Validator transport. File output also writes
`new_view.adaptation_manifest.json`; without --output the manifest is embedded in
stdout. JSON objects/arrays are parsed independently of extension; other UTF-8 text
is a raw-only summary carrier. YAML semantic adaptation is not claimed.

Existing contract/registry/schema/validate commands keep their semantics. Validation
smoke runs once after mapping, using partial_bundle; errors are recorded, not used
to rewrite or retry data. No full Golden semantic verdict is asserted.

## Limits and boundaries

Five Phase 1.3 schema gaps remain untouched: conditional endorsement, typed Argument
unit/denominator/transition evidence, dimensional semantics, selected-edge analyst
evidence scope and Skill promotion evidence. Additional concrete unrepresentable
values/unmapped enums are reported in this phase's gap files. Missing source evidence
is recorded as adaptation loss rather than falsely called a solved schema debt.

The script `verify_phase1_4.py` is bounded engineering acceptance only. It saves raw
test and CLI streams, preserves run_001/run_002 history, compares protected hashes and
emits G01–G39 plus a source/artifact-hashed manifest. Phase 1.5/1.6, Audit Runner,
database/Golden migration, production, Analyst Model and Skills remain unstarted.
