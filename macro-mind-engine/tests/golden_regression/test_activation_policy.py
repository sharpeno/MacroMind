"""Policy 1.0: real closure, reversible exclusion, and synthetic adversarial chains."""

from copy import deepcopy

import pytest
from macromind.compatibility.activation import ActivationEngine, prepare
from macromind.compatibility.detector import digest
from tests.validation.helpers import obj, step

from .conftest import CONTRACT, REGISTRY


@pytest.fixture(scope="module")
def activation():
    return ActivationEngine(CONTRACT, REGISTRY)


def active(result):
    return {x["id"]: x for x in result["active_bundle"]["objects"]}


def test_year_range_is_opaque_reversible_not_exact_datetime():
    raw = {"reference_time": {"start": "2022", "end": "2026"}}
    before = deepcopy(raw)
    transformed, ledger = prepare(raw)
    assert raw == before and ledger[0]["before"] == raw["reference_time"]
    assert transformed["reference_time"]["start"] is None
    assert transformed["reference_time"]["end"] is None
    assert "2022" in transformed["reference_time"]["text"]
    assert "2026" in transformed["reference_time"]["text"]


@pytest.mark.parametrize(
    "value",
    [
        {"start": "yesterday"},
        {"start": "2022", "confidence": 0.5},
        {"start": "2022", "end": None},
        {"start": "2022-03-01"},
    ],
)
def test_unsupported_time_never_guessed(value):
    raw = {"reference_time": value}
    assert prepare(raw) == (raw, [])


def test_source_projection_keeps_segment_as_dependency(activation):
    values = [
        obj("Source", "s"),
        obj("SourceSegment", "seg", source_ref="s"),
        obj("Mechanism", "m"),
        obj("MechanismUsage", "u", mechanism_ref="m", source_refs=["seg"]),
    ]
    result = activation.activate({"objects": values})
    assert active(result)["u"]["source_refs"] == ["s"]
    assert result["source_repairs"][0]["before"] == "seg"
    assert result["source_repairs"][0]["segment_hash"] == digest(active(result)["seg"])
    assert any(x["target"] == "seg" for x in result["evidence_dependencies"]["u"])
    assert not result["validation"]["errors"]


def test_bad_segment_parent_cannot_be_used_or_repaired(activation):
    result = activation.activate(
        {
            "objects": [
                obj("SourceSegment", "seg", source_ref="missing"),
                obj("Mechanism", "m"),
                obj("MechanismUsage", "u", mechanism_ref="m", source_refs=["seg"]),
            ]
        }
    )
    assert "u" not in active(result) and "seg" not in active(result)
    assert not result["source_repairs"]
    assert {x["object_ref"] for x in result["repair_pool"] if "object_ref" in x} >= {"u", "seg"}


def test_cross_sample_prior_deferred_without_rewriting_signal(activation):
    signal = obj(
        "AnalystMethodSignal",
        "ms",
        matched_prior_signal_refs=["GS004/MS01"],
        recurrence_match="partial",
    )
    result = activation.activate({"objects": [signal]})
    assert not active(result)
    assert any(x.get("raw_payload") == signal for x in result["repair_pool"])
    assert result["availability_semantics"] == "NOT_USABLE_NOW_IS_NOT_FALSE_OR_PROVEN_ABSENT"


def test_dependency_failure_propagates_to_conclusions_and_consumers(activation):
    values = [
        obj("Claim", "a", source_refs=["missing"]),
        obj("Claim", "b"),
        obj(
            "Argument",
            "arg",
            premises=["a"],
            steps=[step(premises=["a"], conclusion="b")],
            final_conclusion="b",
        ),
        obj("Assessment", "assessment", target_ref="b"),
        obj("Actor", "independent"),
    ]
    before = deepcopy(values)
    result = activation.activate({"objects": values})
    assert values == before
    assert set(active(result)) == {"independent"}
    assert len(result["closure_rounds"]) >= 2
    assert {x["object_ref"] for x in result["repair_pool"]} == {"a", "b", "arg", "assessment"}


def test_source_segment_loss_after_projection_removes_owner(activation):
    values = [
        obj("Source", "s"),
        obj("SourceSegment", "seg", source_ref="s", source_version_ref="missing-version"),
        obj("Mechanism", "m"),
        obj("MechanismUsage", "u", mechanism_ref="m", source_refs=["seg"]),
    ]
    result = activation.activate({"objects": values})
    assert result["source_repairs"]
    assert "u" not in active(result)
    assert "s" in active(result)


def test_raw_evidence_not_silently_lost_when_schema_has_no_field(activation):
    claim = obj("Claim", "c")
    claim["source_segment_refs"] = ["missing-fragment"]
    result = activation.activate({"objects": [claim]})
    assert "c" not in active(result)
    assert result["repair_pool"][0]["raw_payload"] == claim


def test_original_document_unchanged_and_replay_deterministic(activation):
    doc = {"objects": [obj("Actor", "a")]}
    before = deepcopy(doc)
    first, second = activation.activate(doc), activation.activate(doc)
    assert doc == before
    assert first == second
    sha = first.pop("deterministic_hash")
    assert digest(first) == sha


def test_summary_does_not_pass_by_empty_bundle(activation):
    result = activation.activate("Only a historical summary")
    assert result["status"] == "NO_USABLE_OBJECTS"
    assert not active(result)
    assert result["repair_pool"][0]["status"] == "SUMMARY_ONLY_NOT_USABLE"


@pytest.mark.parametrize("name", ["GS002", "GS003", "GS004", "GS005"])
def test_real_active_closure_and_object_conservation(activation, goldens, name):
    result = activation.activate(goldens[name].raw_document)
    counts = result["counts"]
    assert (
        counts["historical_objects"]
        == counts["active"]
        + counts["initial_quarantine"]
        + counts["dependency_or_validation_deferred"]
    )
    assert counts["active"] > 0
    assert not result["validation"]["errors"]
    assert not [
        i for i in result["validation"]["indeterminate"] if i["rule_id"].startswith("V-REF")
    ]
    for identity in active(result):
        assert all(
            edge["target"] in active(result) for edge in result["evidence_dependencies"][identity]
        )
    if name == "GS004":
        assert len(result["source_repairs"]) == 12
        assert not any(
            i["object_type"] == "IndicatorObservation" and i["id"] == "OB20" and i["unit"] == "pp"
            for i in active(result).values()
        )
    if name == "GS005":
        assert "C092" in active(result)
        assert not any(
            i["object_type"] == "Forecast" and i["claim_ref"] == "C005"
            for i in active(result).values()
        )
        assert any(
            i["object_type"] == "Scenario" and "C005" in i["claim_refs"]
            for i in active(result).values()
        )
        assert result["raw_document"]["finalization"]["completed"] is False
