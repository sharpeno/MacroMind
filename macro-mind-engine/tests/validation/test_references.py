import pytest

from .helpers import has, obj


def test_duplicate_unknown_and_invalid_targets(engine):
    claim = obj("Claim")
    assert has(engine.validate([claim, claim]), "V-REF001", "ERROR")
    strange = dict(claim, object_type="Geography")
    assert has(engine.validate([strange]), "V-REF002", "ERROR")
    bad = obj("Source", "source")
    del bad["title"]
    report = engine.validate([obj("Claim", source_refs=["source"]), bad])
    assert has(report, "V-SCH002", "ERROR")
    assert has(report, "V-REF004", "INDETERMINATE")


@pytest.mark.parametrize(
    "mode,outcome", [("complete_bundle", "ERROR"), ("partial_bundle", "INDETERMINATE")]
)
def test_modes(engine, mode, outcome):
    report = engine.validate([obj("Claim", source_refs=["missing"])], {"validation_mode": mode})
    assert has(report, "V-REF004" if mode == "complete_bundle" else "V-REF005", outcome)
    if mode == "partial_bundle":
        assert not report.errors


@pytest.mark.parametrize(
    "kind,field,target",
    [
        ("Source", "version_refs", "SourceVersion"),
        ("Source", "segment_refs", "SourceSegment"),
        ("Source", "family_ref", "SourceFamily"),
        ("Claim", "source_refs", "Source"),
        ("StructuralProcess", "event_refs", "Event"),
        ("StructuralProcess", "observation_refs", "IndicatorObservation"),
        ("StructuralProcess", "policy_refs", "Policy"),
        ("Policy", "actor_refs", "Actor"),
        ("Policy", "event_refs", "Event"),
        ("Event", "policy_refs", "Policy"),
        ("Forecast", "claim_ref", "Claim"),
        ("Assessment", "information_set_ref", "InformationSet"),
        ("MechanismUsage", "mechanism_ref", "Mechanism"),
        ("ClaimOccurrence", "claim_ref", "Claim"),
        ("ClaimOccurrence", "source_segment_ref", "SourceSegment"),
        ("ClaimOccurrence", "source_version_ref", "SourceVersion"),
        ("ClaimOccurrence", "origin_family_ref", "SourceFamily"),
    ],
)
def test_reference_contracts(engine, kind, field, target):
    value = ["target"] if field.endswith("_refs") else "target"
    source = obj(kind, **{field: value})
    report = engine.validate(
        [source, obj("Thesis", "target")], {"validation_mode": "partial_bundle"}
    )
    assert has(report, "V-REF003", "ERROR")
    report = engine.validate([source, obj(target, "target")], {"validation_mode": "partial_bundle"})
    assert not any(
        i.outcome == "ERROR"
        and i.object_ref == source["id"]
        and i.field_path.startswith("/" + field)
        for i in report.issues
        if i.rule_id == "V-REF003"
    )


def test_only_explicit_self_reference_forbidden(engine):
    signal = obj("AnalystMethodSignal", "s", matched_prior_signal_refs=["s"])
    assert has(engine.validate([signal]), "V-REF006", "ERROR")
    source = obj("Source", "source")
    source["provenance_refs"] = ["source"]
    assert not has(engine.validate([source]), "V-REF006", "ERROR")


def test_asymmetric_policy_event_is_valid(engine):
    report = engine.validate([obj("Policy", event_refs=["e"]), obj("Event", "e")])
    assert not report.errors
