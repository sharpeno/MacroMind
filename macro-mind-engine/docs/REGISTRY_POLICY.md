# Registry policy

`registries/v0_3/*.yaml` is the single source of vocabulary authority. The files use
JSON-compatible YAML (valid YAML, all strings explicitly quoted). Loading uses a
SafeLoader subclass that also rejects duplicate keys. Enum generation is a build
step, not a second authority: generated `_enums.py` is marked DO NOT EDIT and must
match source bytes generated deterministically. `load_registry` rejects stale or
incompatible generated enums. Schema enum use is tested against this bundle.

Object kinds are core, auxiliary, analyst_auxiliary or governance. Core membership
must exactly equal the frozen 14. The 12 auxiliary schemas include SourceFamily;
ReviewQueueItem represents a queue item, not a new Core. No automatic promotion
exists. Base and nested schema structures are not object types.

The MA.1 comparison, role, stage, recurrence, failure and verification vocabulary
is preserved. Observed GS004/005 expression/context/signal values are included.
`unknown` additions and minimal value-kind, review and heuristic vocabularies are
candidate implementation extensions. Stable vocabulary entries mean accepted
spelling/meaning, not validated facts or production readiness. Text fields without
an agreed finite taxonomy remain text; no hidden enum is duplicated in a model.

All nine relation contracts are candidate, with explicit source/target types and
frozen evidence references. ASSERTED_BY, SUPPORTED_BY, DERIVED_FROM, OBSERVED_AS,
USES_MECHANISM, REFERS_TO, CONTRADICTS, PART_OF and VERSION_OF represent evidenced
links. CONTRADICTS is a claim disagreement, not a structural Contradiction object.
LOCATED_IN was considered but deferred: no Geography model/registry exists in the
requested minimum set; Actor.location currently preserves location as a field.
INSTANCE_OF was considered but deferred pending an evidenced type-instance
contract; speculative endpoints would create false precision. These are not
silently declared stable relations.

Schema 0.1.0 is registered against ontology 0.3. PATCH adjusts non-breaking
implementation/metadata; MINOR extends compatible fields/enums; MAJOR can break
schemas. None automatically upgrades the frozen ontology. To extend a vocabulary:
edit YAML, regenerate Python enums, restart the importing Python process, export
schemas, update the schema version as appropriate, then run the gates. Regeneration
is never triggered while loading user data. Deprecation preserves a legal,
non-deprecated replacement; duplicate values and inconsistent metadata fail closed.

Identity policies cover Actor, Source, SourceFamily, Mechanism and Indicator.
Evidence is required for alias/origin matching; names or URL equality alone do not
merge records. This phase defines policies only. Entity resolution and exhaustive
cross-Golden identity coverage remain outstanding D07 work.

