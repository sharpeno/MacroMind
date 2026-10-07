from copy import deepcopy

import pytest
from macromind.validation import ValidationContext, ValidationInput, ValidationInputError
from macromind.validation.catalog import RULES, rule_catalog
from macromind.validation.index import MODEL_TYPES

from .helpers import has, obj


def test_catalog_deterministic_and_all_rules_executed(engine):
    first = engine.validate({"objects": []})
    assert first == engine.validate({"objects": []})
    assert len(RULES) == len(set(r.rule_id for r in RULES)) == first.executed_rule_count
    assert len(first.rule_results) == first.rule_count
    assert {i.rule_id for i in first.issues} == {r.rule_id for r in RULES}
    assert rule_catalog() == rule_catalog()
    assert not first.errors and first.not_applicable
    assert sum(first.outcome_counts.values()) == len(first.issues)


@pytest.mark.parametrize("kind", sorted(MODEL_TYPES))
def test_all_registered_canonical_types_load(engine, kind):
    report = engine.validate([obj(kind)], {"validation_mode": "partial_bundle"})
    assert not has(report, "V-SCH002", "ERROR")
    assert not has(report, "V-SCH001", "ERROR")


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"objects": [None]},
        {"objects": [], "other": True},
        {"objects": [{"metadata": {"bad": float("nan")}}]},
    ],
)
def test_transport_errors(engine, payload):
    with pytest.raises(ValidationInputError):
        engine.validate(payload)


@pytest.mark.parametrize(
    "context",
    [
        [],
        "",
        {"validation_mode": "guess"},
        {"ontology_version": "0.2"},
        {"time_overrides": {"ref": "last autumn"}},
    ],
)
def test_context_errors(engine, context):
    with pytest.raises(ValidationInputError):
        engine.validate([], context)


def test_legacy_missing_fields_extra_fields(engine):
    old = obj("Claim", schema_version="0.1.0")
    old["schema_version"] = "legacy"
    report = engine.validate([old])
    assert has(report, "V-SCH001", "ERROR")
    assert any(i.message == "unsupported_schema_version" for i in report.errors)
    value = obj("Claim")
    del value["statement"]
    assert has(engine.validate([value]), "V-SCH002", "ERROR")
    thesis = obj("Thesis")
    thesis["prediction_window"] = None
    assert has(engine.validate([thesis]), "V-SCH002", "ERROR")


def test_snapshot_and_supported_inputs(engine):
    value = obj("Claim")
    before = deepcopy(value)
    a = engine.validate(ValidationInput(objects=[value]), ValidationContext())
    b = engine.validate([MODEL_TYPES["Claim"].model_validate(value)])
    assert a == b and value == before
    assert a.deterministic_hash == engine.validate([value]).deterministic_hash


def test_semantic_hash_changes_with_context_and_input(engine):
    a = engine.validate([obj("Claim")])
    assert (
        a.deterministic_hash
        != engine.validate([obj("Claim", statement="different")]).deterministic_hash
    )
    assert (
        a.deterministic_hash
        != engine.validate(
            [obj("Claim")], {"knowledge_cutoff": "2026-01-01T00:00:00Z"}
        ).deterministic_hash
    )
