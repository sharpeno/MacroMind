# Phase 1.3 Validator architecture

Ontology 0.3 remains FROZEN. Schema, registry and validator versions are 0.1.0.
The validator accepts canonical objects, detects structural conflicts and preserves
unknown values. It neither repairs input nor determines whether a claim is true.

## Runtime API and execution

`ValidatorEngine(contract_root, registry_root).validate(input, context)` verifies the
actual frozen contract and registry on construction. Input may be an internal
`ValidationInput`, a JSON envelope `{"objects": [...]}`, or a list of canonical
dictionaries/Pydantic objects. Raw objects must explicitly identify canonical schema
and ontology versions. Unsupported versions produce `unsupported_schema_version`;
there is no legacy conversion. Transport/context errors raise `ValidationInputError`.

The engine deep-copies the transport, builds an ObjectIndex, validates each object
through the registered Pydantic class, and executes every catalog rule. Duplicate
ids are never resolved arbitrarily. Invalid targets remain unavailable; their
dependent checks are indeterminate while their primary errors remain errors.
The raw and modeled snapshots are checked after all rules to detect rule mutation.
Unexpected execution errors propagate; they are never converted into PASS.

ValidationInput, ValidationContext, ObjectIndex, reports and rule outcomes are
internal runtime types. They do not appear in object_types.yaml or schema exports.
No runtime framework, network access, LLM, embeddings or text classification is used.

## References

`reference_contracts.py` centrally declares each supported field, target types,
resolution mode and explicit self-reference prohibition. An unspecified target
taxonomy means local existence only; the validator does not invent a narrower type.
Attribution identifiers and provenance_refs are external identities. Argument node
references may use local step ids or registered object ids. Fragile-step references
accept step ids and documented local paths (`steps/0`, `/steps/0`, `#/steps/0`,
`argument-id/steps/0`). A step id denotes its inference result; no global id is renamed.
Scenario child references resolve within its branch list. No reciprocal Policy/Event
edge is required. Only active prior self-reference is explicitly prohibited.
Local step/global object id collisions make graph interpretation indeterminate;
they are not used to invent a cycle or choose an arbitrary target.

Absent local refs are ERROR in complete_bundle and INDETERMINATE in partial_bundle.
Wrong target types and duplicate ids remain ERROR in both modes. No Review state
changes any rule execution or severity.

## Time and evidence

TimeReference comparisons require both timezone-aware start and end. A known instant
can be recorded as start == end. An omitted endpoint, naive timestamp, unknown value,
plain temporal text or overlapping intervals cannot prove ordering. Context datetime
overrides are explicit instants. No missing endpoint or timezone is inferred.
Content time comes from a signal's explicitly referenced SourceSegment/SourceVersion
chain or context override. Publication/capture do not substitute for content time.
A prior wholly after either explicit cutoff or current content interval is ERROR.
Unknown/overlapping order is INDETERMINATE. No sample id, number or filename is time.

Argument steps form a directed graph between premise, inference and conclusion nodes.
Cycles are ERROR; incomplete/disconnected steps require review. These are structural
checks, not economic correctness judgments. Every edge keeps its own reasoner,
analysis_context and expression_level, independently of the overall Argument.
Explicit model reconstruction used as analyst evidence is ERROR with review; a mixed
Argument citation is WARNING because selected-edge evidence scope is absent.

Forecast admission distinguishes invalid structure, indeterminate evidence and
structurally supported admission. Even the last is not a semantic endorsement verdict.
Conditional endorsement lacks a structured representation and remains indeterminate,
including when free-text branch selection exists. Scenario stays Scenario. Resolution
timing and scoring permission are not inferred from admission or vice versa.

## Deterministic reports

All 37 registered rules run in fixed category order: Schema, Reference, Provenance,
Temporal, Boundary, Forecast, Argument, Analyst, Governance. No applicable object or
mode yields an explicit NOT_APPLICABLE finding. `rule_results` aggregates each rule's
findings using ERROR > WARNING > INDETERMINATE > PASS > NOT_APPLICABLE.
`executed_rule_count` includes explicit NOT_APPLICABLE executions.

`issues` is the full audit stream, including PASS and NOT_APPLICABLE. `outcome_counts`
counts findings, not objects or rules. Separate errors, warnings, indeterminate and
not_applicable arrays are exact filtered subsets; indeterminate never counts as ERROR.
Findings sort by rule_id, object_ref, field_path, then full canonical finding JSON.
The hash covers canonical JSON report content except its own hash, including input,
context, frozen semantic and registry semantic hashes. `sample_label` is excluded
from semantic context; it has no validation role. Wall clock and run id occur only in
CLI stderr logs. Identical inputs produce byte-equivalent semantic reports. Renaming
object references changes reported identities/hash, but cannot change chronology
outcomes when timestamps are unchanged.

## CLI

```powershell
macromind validate --input canonical_bundle.json --contract-root ../golden_sample_test/core_ontology/v0.3 --registry-root registries/v0_3 --context validation_context.json --mode complete_bundle
```

Input and both roots are required. Context is optional. Explicit --mode overrides
context.validation_mode; otherwise context or complete_bundle applies. Stdout is
ValidationReport JSON, stderr is an operational log. Exit 0 means no ERROR (warnings
and indeterminate allowed), 1 means semantic errors, 2 means malformed input/context,
usage or unavailable/incompatible configuration. Missing command options still exit 2.

## Scope and acceptance

Five explicit schema gaps preserve uncertainty: conditional endorsement, Argument
transition semantics, controlled comparison units/denominators, selected-edge analyst
evidence scope and Skill promotion evidence. They do not block Phase 1.3 because the
Prompt explicitly permits indeterminate outcomes and prohibits inventing these fields.
No missing current registry vocabulary was found. Precision missing in a particular
record is a data limitation, not automatically a schema gap.

`scripts/verify_phase1_3.py` is a bounded engineering acceptance check for this phase,
not a general domain Audit Runner. It runs synthetic tests, the unchanged prior suite,
installed CLI checks, protected-file hashes and G01–G29. It never validates or migrates
the full Golden bundles. Raw subprocess outputs and JUnit reports are retained under
phase1. Phase 1.4, production import, Skill compilation and Batch Pilot remain unstarted.
