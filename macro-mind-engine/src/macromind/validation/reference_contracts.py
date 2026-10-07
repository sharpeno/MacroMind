"""Reference field authority for validator resolution, not new ontology definitions.

None target_types means unspecified by the current schema: verify local existence
without guessing a narrower target type. Attribution/provenance identities are
external references, not necessarily ontology objects. Argument node refs additionally
allow a local step result. Only an active prior referring to itself is forbidden.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceContract:
    field: str
    target_types: tuple[str, ...] | None
    resolution: str = "local"
    allow_self: bool = True


def spec(field, *types, resolution="local", allow_self=True):
    return ReferenceContract(field, types or None, resolution, allow_self)


REFERENCE_CONTRACTS = {
    "Source": [
        spec("version_refs[]", "SourceVersion"),
        spec("segment_refs[]", "SourceSegment"),
        spec("family_ref", "SourceFamily"),
    ],
    "Claim": [spec("source_refs[]", "Source")],
    "Event": [
        spec("evidence_refs[]"),
        spec("actor_refs[]", "Actor"),
        spec("policy_refs[]", "Policy"),
    ],
    "StructuralProcess": [
        spec("event_refs[]", "Event"),
        spec("observation_refs[]", "IndicatorObservation"),
        spec("policy_refs[]", "Policy"),
        spec("evidence_refs[]"),
    ],
    "Actor": [spec("identity_evidence_refs[]", resolution="external")],
    "Indicator": [spec("source_refs[]", "Source")],
    "Policy": [
        spec("source_refs[]", "Source"),
        spec("event_refs[]", "Event"),
        spec("actor_refs[]", "Actor"),
    ],
    "Mechanism": [spec("source_refs[]", "Source")],
    "Argument": [
        spec("premises[]", resolution="argument_node"),
        spec("intermediate_conclusions[]", resolution="argument_node"),
        spec("final_conclusion", resolution="argument_node"),
        spec("steps[].premises[]", resolution="argument_node"),
        spec("steps[].conclusion_ref", resolution="argument_node"),
        spec("steps[].source_refs[]", "Source"),
        spec("source_refs[]", "Source"),
        spec("most_fragile_step[]", resolution="local_step"),
    ],
    "Thesis": [
        spec("argument_refs[]", "Argument"),
        spec("event_refs[]", "Event"),
        spec("process_refs[]", "StructuralProcess"),
        spec("indicator_refs[]", "Indicator"),
        spec("supporting_evidence_refs[]"),
        spec("counterevidence_refs[]"),
    ],
    "Forecast": [spec("claim_ref", "Claim"), spec("source_refs[]", "Source")],
    "Contradiction": [spec("event_refs[]", "Event"), spec("thesis_refs[]", "Thesis")],
    "Assessment": [spec("target_ref"), spec("information_set_ref", "InformationSet")],
    "Heuristic": [spec("counterexamples[]"), spec("provenance[]")],
    "SourceVersion": [spec("source_ref", "Source"), spec("source_refs[]", "Source")],
    "SourceSegment": [spec("source_ref", "Source"), spec("source_version_ref", "SourceVersion")],
    "SourceFamily": [spec("source_refs[]", "Source"), spec("evidence_refs[]")],
    "ClaimOccurrence": [
        spec("claim_ref", "Claim"),
        spec("source_segment_ref", "SourceSegment"),
        spec("source_version_ref", "SourceVersion"),
        spec("origin_family_ref", "SourceFamily"),
    ],
    "TranscriptCorrection": [
        spec("source_segment_ref", "SourceSegment"),
        spec("source_refs[]", "Source"),
    ],
    "IndicatorObservation": [
        spec("indicator_ref", "Indicator"),
        spec("source_refs[]", "Source"),
        spec("comparison_basis.baseline_source_ref", "Source"),
    ],
    "InformationSet": [spec("source_version_refs[]", "SourceVersion"), spec("content_refs[]")],
    "ExpectationSnapshot": [spec("source_refs[]", "Source")],
    "Scenario": [
        spec("claim_refs[]", "Claim"),
        spec("source_refs[]", "Source"),
        spec("branches[].child_branch_refs[]", resolution="scenario_branch"),
    ],
    "ReviewQueueItem": [spec("target_ref")],
    "AnalystMethodSignal": [
        spec("source_segment_refs[]", "SourceSegment"),
        spec("argument_refs[]", "Argument"),
        spec("claim_refs[]", "Claim"),
        spec("matched_prior_signal_refs[]", "AnalystMethodSignal", allow_self=False),
        spec("recurrence_evidence[]"),
    ],
    "MechanismUsage": [
        spec("mechanism_ref", "Mechanism"),
        spec("source_refs[]", "Source"),
        spec("argument_refs[]", "Argument"),
    ],
}
EXTERNAL_FIELDS = (
    "provenance_refs[]",
    "reasoner_id",
    "analyst_id",
    "annotation_observer",
    "observer",
    "observed_reasoner_id",
    "steps[].reasoner_id",
)


def values(obj, expression):
    def walk(value, parts, path):
        if not parts:
            if isinstance(value, str):
                yield path, value
            return
        part, *rest = parts
        many = part.endswith("[]")
        key = part[:-2] if many else part
        value = getattr(value, key, None)
        if many:
            if isinstance(value, list):
                for i, item in enumerate(value):
                    yield from walk(item, rest, f"{path}/{key}/{i}")
        else:
            yield from walk(value, rest, f"{path}/{key}")

    yield from walk(obj, expression.split("."), "")


def references(obj):
    for contract in REFERENCE_CONTRACTS.get(obj.object_type, []):
        for path, ref in values(obj, contract.field):
            yield contract, path, ref
