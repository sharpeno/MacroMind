# Adapter policy — Phase 1.4

Compatibility version 0.1.0 targets Ontology 0.3, Schema/Registry/Validator 0.1.0.

- No LLM, semantic reconstruction, date parsing, hindsight enrichment or adjudication.
- No in-place mutation, overwrite, rename or deletion of historical inputs. Existing
  output files and input/output aliases (including hardlinks) are rejected.
- Unknown > Guess. Missing nullable/unknown-capable fields receive documented unknown,
  null or empty lists according to the unchanged schema. Explicit null is preserved
  only where valid. Missing required semantics with no safe representation quarantine
  the object. Missing nonsemantic defaults are explicitly recorded.
- Every emitted canonical leaf has a mapping entry, operation, reason and value hash.
  Input pointers refer to the immutable raw_document; output pointers refer to the
  AdaptationResult. Nested representation changes may cite their containing source
  structure. No mapping has semantic_change=true.
- Unsupported fields and section layouts remain verbatim in raw_document, with
  PRESERVE_RAW mapping and explicit loss records. Quarantine embeds raw payloads and
  hashes. Raw preservation is not permission to treat those values as active facts.
- Accepted human decisions are preserved from the selected artifact itself. The
  engine does not merge a later artifact into an earlier one. Artifact selection uses
  accepted metadata and content-hash-linked finalization/hotfix records, never mtime.
  Explicit machine_use_policy excluded occurrence ids and immutable object quarantine
  lists remain quarantined; their payloads never become active canonical evidence.
- Sources, Claims, Scenarios, Forecasts, Mechanisms and MethodSignals remain their
  explicit section types. Text is never used to reclassify objects. A recorded Scenario
  condition/outcome can be wrapped as a branch; that does not endorse a forecast.
- Time strings become opaque TimeReference.text, never parsed bounds. Video offsets
  do not become assertion dates. Missing reasoners are never inherited from parents.
- Only explicit representation-equivalent enum aliases are mapped. Unknown enum
  spellings preserve raw data plus ENUM_UNMAPPED loss and use unknown if allowed.
  No vocabulary is added, and no unit, delta, baseline or financial role is inferred.
- Summary/text-only carriers remain PARTIAL with no reconstructed domain objects.

LOSSLESS requires no loss, newly defaulted unknown, quarantine or unsupported field.
LOSSY_BUT_SAFE preserves the history but has representational limitations. PARTIAL
allows useful canonical objects alongside quarantines or Validator semantic errors.
UNSUPPORTED means no safe adapter/shape/target or no safely representable objects.
No retry changes canonical semantics in response to Validator errors.

Canonical transport validation is separate from historical correctness. Validator
semantic errors are retained in validator_report_summary, not repaired or suppressed.
All adapted historical bundles recommend partial_bundle because external identities
and cross-artifact references are intentionally not filled from other artifacts.
