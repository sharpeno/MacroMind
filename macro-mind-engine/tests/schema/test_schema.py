import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from macromind.contract.version import CORE_NAMES
from macromind.registry._enums import ENUM_TYPES
from macromind.schema.auxiliary import (
    AUXILIARY_MODELS,
    IndicatorObservation,
    MechanismUsage,
    Scenario,
)
from macromind.schema.base import MacroMindObjectBase
from macromind.schema.common import ComparisonBasis, UnknownValue
from macromind.schema.core import (
    CORE_MODELS,
    Argument,
    Assessment,
    Claim,
    Forecast,
    Indicator,
    Mechanism,
)
from macromind.schema.export import export_schemas, schema_artifacts
from pydantic import ValidationError


def sample(model):
    # Explicit synthetic structural fixtures; never invented Golden objects.
    schema = model.model_json_schema()

    def fill(s):
        if "$ref" in s:
            return fill(schema["$defs"][s["$ref"].split("/")[-1]])
        if "const" in s:
            return s["const"]
        if "enum" in s:
            return "unknown" if "unknown" in s["enum"] else s["enum"][0]
        if "anyOf" in s:
            if any(o.get("type") == "null" for o in s["anyOf"]):
                return None
            return fill(s["anyOf"][0])
        if s.get("type") == "array":
            return []
        if s.get("type") == "object":
            return {k: fill(v) for k, v in s["properties"].items() if k in s.get("required", [])}
        if s.get("type") in ("number", "integer"):
            return 0
        return "synthetic"

    return fill(schema)


def test_S001_models():
    assert set(CORE_MODELS) == set(CORE_NAMES)
    assert len(AUXILIARY_MODELS) == 12


@pytest.mark.parametrize("model", list(CORE_MODELS.values()) + list(AUXILIARY_MODELS.values()))
def test_S002_S003_S013_models_and_jsonschema(model):
    data = sample(model)
    obj = model.model_validate(data)
    assert obj.schema_version == "0.1.0"
    schema = model.model_json_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(obj.model_dump(mode="json"))
    with pytest.raises(ValidationError):
        model.model_validate(data | {"ontology_version": "0.4"})
    with pytest.raises(ValidationError):
        model.model_validate(data | {"schema_version": "99.0.0"})
    with pytest.raises(ValidationError):
        model.model_validate(data | {"object_type": "Other"})


def test_S004_S005_unknown_and_invalid_enum():
    for enum in ENUM_TYPES.values():
        assert enum("unknown").value == "unknown"
        with pytest.raises(ValueError):
            enum("invented_value")
    data = sample(IndicatorObservation)
    with pytest.raises(ValidationError):
        IndicatorObservation.model_validate(data | {"semantic_role": "not_registered"})
    obj = IndicatorObservation.model_validate(data | {"value": {"state": "unknown"}})
    assert obj.value == UnknownValue()
    assert IndicatorObservation.model_validate(data | {"value": None}).value is None
    data.pop("value")
    with pytest.raises(ValidationError):
        IndicatorObservation.model_validate(data)


def test_S006_S007_S008_separation():
    assert not issubclass(Scenario, Forecast)
    assert not issubclass(MechanismUsage, Mechanism)
    assert not issubclass(IndicatorObservation, Indicator)


def test_S009_claim_dimensions():
    data = sample(Claim) | {
        "claimant": "speaker",
        "population": "households",
        "quantifier": "some",
        "asserted_at": {"text": "September 2026"},
        "reference_time": {"text": "2025"},
        "modal_strength": "may",
        "reasoner_id": "analyst",
    }
    claim = Claim.model_validate(data)
    assert claim.asserted_at != claim.reference_time
    assert claim.population == "households" and claim.modal_strength == "may"


def test_S010_forecast_unknowns_and_resolution():
    data = sample(Forecast) | {
        "knowledge_cutoff": {"text": "2026-09-01"},
        "prediction_window": {"state": "unknown"},
        "resolution_criteria": {
            "description": "reported outcome",
            "reasoner_id": "model",
            "analysis_context": "model_diagnostic",
            "set_at": None,
            "approved_at": None,
            "evaluation_time": None,
            "scoring_permitted": None,
        },
    }
    obj = Forecast.model_validate(data)
    assert obj.resolution_criteria.scoring_permitted is None
    assert obj.prediction_window == UnknownValue()


def test_S011_assessment_no_truth_mutation():
    obj = Assessment.model_validate(sample(Assessment))
    assert "truth" not in type(obj).model_fields
    with pytest.raises(ValidationError):
        Assessment.model_validate(sample(Assessment) | {"truth": True})


def test_S012_argument_per_edge_attribution():
    step = {
        "id": "e1",
        "premises": ["c1"],
        "conclusion_ref": "c2",
        "statement": "possible link",
        "expression_level": "model_reconstruction",
        "reasoner_id": "model",
        "analysis_context": "model_diagnostic",
        "source_refs": [],
    }
    obj = Argument.model_validate(sample(Argument) | {"reasoner_id": "analyst", "steps": [step]})
    assert obj.steps[0].reasoner_id != obj.reasoner_id


def test_S014_export_deterministic(tmp_path):
    first = export_schemas(tmp_path / "one")
    second = export_schemas(tmp_path / "two")
    assert first == second
    for relative, payload in schema_artifacts().items():
        assert (
            (tmp_path / "one" / relative).read_bytes()
            == (tmp_path / "two" / relative).read_bytes()
            == payload
        )
    for entry in first["schemas"]:
        assert (
            hashlib.sha256((tmp_path / "one" / entry["path"]).read_bytes()).hexdigest()
            == entry["sha256"]
        )
        Draft202012Validator.check_schema(
            json.loads((tmp_path / "one" / entry["path"]).read_text(encoding="utf-8"))
        )


def test_comparison_never_calculates_delta():
    obj = ComparisonBasis(
        comparison_type="yoy",
        baseline_value=100,
        baseline_period=None,
        baseline_source_ref=None,
        delta_value=None,
        delta_unit=None,
    )
    assert obj.delta_value is None


def test_fields_document_origins():
    for model in [MacroMindObjectBase, *CORE_MODELS.values(), *AUXILIARY_MODELS.values()]:
        for field in model.model_fields.values():
            assert field.json_schema_extra["field_origin"] in {
                "frozen_semantic_requirement",
                "validated_auxiliary_contract",
                "implementation_extension",
            }


def test_S015_frozen_unchanged(contract_root):
    from macromind.contract.loader import load_frozen_contract

    assert load_frozen_contract(contract_root).integrity_report.status == "PASS"


def test_mapping_covers_core_models():
    mapping = Path(__file__).resolve().parents[2] / "docs/SCHEMA_MAPPING.md"
    text = mapping.read_text(encoding="utf-8")
    for name in CORE_MODELS:
        assert f"## {name}\n" in text
