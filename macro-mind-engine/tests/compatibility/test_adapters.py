from copy import deepcopy

from macromind.compatibility.engine import MODELS

from .helpers import canonical, legacy


def test_copy_rename_unknown_immutable(compatibility):
    value = legacy(
        [{"claim_id": "c", "statement": "Words", "claimant_id": "author", "reasoner_id": "model"}]
    )
    before = deepcopy(value)
    result = compatibility.adapt(value)
    claim = canonical(result, "Claim")[0]
    assert claim["id"] == "c" and claim["statement"] == "Words" and claim["claimant"] == "author"
    assert claim["reasoner_id"] == "model" and claim["annotation_observer"] is None
    assert claim["population"] == {"state": "unknown"}
    assert value == before and result.raw_document == value
    operations = {m.operation for m in result.mapping_ledger}
    assert {"COPY", "RENAME", "DEFAULT_UNKNOWN"} <= operations
    assert result.unknowns and result.losses and result.status != "LOSSLESS"


def test_enum_map_and_unknown_enum(compatibility):
    value = legacy()
    value["25_CANDIDATE_HEURISTICS"] = [
        {"heuristic_id": "h", "status": "observed_candidate_only", "rule": "Recorded candidate"}
    ]
    result = compatibility.adapt(value)
    assert canonical(result, "Heuristic")[0]["status"] == "candidate"
    assert any(m.operation == "ENUM_MAP" for m in result.mapping_ledger)
    value["25_CANDIDATE_HEURISTICS"][0]["status"] = "unknown_unmapped_spelling"
    result = compatibility.adapt(value)
    assert canonical(result, "Heuristic")[0]["status"] == "unknown"
    assert any(item.category == "ENUM_UNMAPPED" for item in result.losses)


def test_required_semantics_quarantine(compatibility):
    value = legacy()
    value["03_SOURCE_VERSIONS"] = [{"source_version_id": "v"}]
    result = compatibility.adapt(value)
    assert result.status == "PARTIAL" and result.quarantined_object_count == 1
    assert "source_ref" in result.quarantined_items[0].missing_semantics
    assert result.quarantined_items[0].raw_payload == value["03_SOURCE_VERSIONS"][0]
    assert any(item.severity == "BLOCKING" for item in result.losses)


def test_scenario_not_forecast(compatibility):
    value = legacy()
    value["21_SCENARIOS"] = [
        {
            "scenario_id": "branch",
            "claim_refs": ["c"],
            "condition": "if",
            "result": "possible",
            "forecast_admitted": False,
        }
    ]
    result = compatibility.adapt(value)
    assert canonical(result, "Scenario")[0]["branches"][0]["condition"] == "if"
    assert not canonical(result, "Forecast")
    assert any(
        u["source_path"].endswith("/forecast_admitted") and u["value"] is False
        for u in result.unsupported_fields
    )


def test_no_temporal_parsing_or_claim_source_fabrication(compatibility):
    value = legacy([{"claim_id": "c", "statement": "Recorded", "asserted_at": "last autumn"}])
    claim = canonical(compatibility.adapt(value), "Claim")[0]
    assert claim["asserted_at"] == {
        "text": "last autumn",
        "start": None,
        "end": None,
        "source_ref": None,
    }
    assert claim["source_refs"] == []


def test_argument_per_edge_no_attribution_inheritance(compatibility):
    value = legacy([{"claim_id": "a", "statement": "A"}, {"claim_id": "b", "statement": "B"}])
    value["18_ARGUMENTS"] = [
        {
            "argument_id": "arg",
            "reasoner_id": "analyst",
            "steps": [
                {
                    "from_claim": "a",
                    "to_claim": "b",
                    "expression_level": "model_reconstruction",
                    "reasoner_id": "model",
                }
            ],
        }
    ]
    result = compatibility.adapt(value)
    argument = canonical(result, "Argument")[0]
    assert argument["reasoner_id"] == "analyst" and argument["steps"][0]["reasoner_id"] == "model"
    assert argument["steps"][0]["premises"] == ["a"]


def test_every_emitted_object_is_canonical(real_results):
    for result in real_results.values():
        for value in result.canonical_bundle["objects"]:
            assert MODELS[value["object_type"]].model_validate(value)


def test_canonical_pass_through_can_be_lossless(compatibility):
    canonical_bundle = compatibility.adapt(legacy()).canonical_bundle
    result = compatibility.adapt(canonical_bundle)
    assert result.source_family == "CANONICAL_0_1"
    assert result.status == "LOSSLESS"
    assert result.canonical_bundle == canonical_bundle
    assert not result.losses and not result.unknowns and not result.quarantined_items
