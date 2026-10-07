from .helpers import legacy


def test_unknown_fields_preserved_and_loss_reported(compatibility):
    value = legacy(
        [{"claim_id": "c", "statement": "known", "unsupported_meaning": {"nested": [1, "two"]}}]
    )
    result = compatibility.adapt(value)
    assert result.raw_document == value
    unsupported = [
        u for u in result.unsupported_fields if u["source_path"].endswith("/unsupported_meaning")
    ]
    assert unsupported and unsupported[0]["value"] == {"nested": [1, "two"]}
    assert any(
        item.source_path == unsupported[0]["source_path"] and item.preserved_raw
        for item in result.losses
    )
    assert any(m.operation == "PRESERVE_RAW" for m in result.mapping_ledger)


def test_null_unknown_missing_remain_distinct(compatibility):
    value = legacy(
        [
            {"claim_id": "a", "statement": "A", "population": None},
            {"claim_id": "b", "statement": "B", "population": {"state": "unknown"}},
            {"claim_id": "c", "statement": "C"},
        ]
    )
    result = compatibility.adapt(value)
    by_id = {o["id"]: o for o in result.canonical_bundle["objects"]}
    assert by_id["a"]["population"] is None
    assert by_id["b"]["population"] == by_id["c"]["population"] == {"state": "unknown"}
    assert any(
        m.operation == "DEFAULT_UNKNOWN" and "/objects/2/population/state" in m.target_path
        for m in result.mapping_ledger
    )
    assert "population" not in result.raw_document["08_CLAIMS"][2]


def test_required_claim_statement_is_never_fabricated(compatibility):
    value = legacy(
        [
            {"claim_id": "a", "statement": None},
            {"claim_id": "b", "statement": {"state": "unknown"}},
            {"claim_id": "c"},
        ]
    )
    result = compatibility.adapt(value)
    assert result.canonical_object_count == 0 and result.quarantined_object_count == 3
    assert result.status == "UNSUPPORTED"
