from .helpers import canonical, legacy


def test_explicit_historical_exclusion_is_id_independent(compatibility):
    value = legacy(ma1=True)
    value["09_CLAIM_OCCURRENCES"] = [
        {"occurrence_id": "arbitrary-occurrence", "claim_id": "c", "source_segment_ref": "segment"}
    ]
    value["ma1_migration"]["machine_use_policy"] = {
        "excluded_occurrence_evidence": ["arbitrary-occurrence"]
    }
    result = compatibility.adapt(value)
    assert not canonical(result, "ClaimOccurrence")
    assert any(q.reason_code == "explicit_historical_exclusion" for q in result.quarantined_items)
    value["ma1_migration"]["machine_use_policy"]["excluded_occurrence_evidence"] = []
    assert canonical(compatibility.adapt(value), "ClaimOccurrence")


def test_explicit_immutable_quarantine_is_not_overturned(compatibility):
    value = legacy(ma1=True)
    value["ma1_migration"]["machine_use_policy"] = {"immutable_object_quarantine": ["c"]}
    result = compatibility.adapt(value)
    assert not canonical(result, "Claim")
    assert result.quarantined_items[0].reason_code == "explicit_historical_exclusion"
