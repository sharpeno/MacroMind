"""Rebuild the auditable field map from the verified contract and executable models."""

from pathlib import Path

from macromind.contract.loader import load_frozen_contract
from macromind.schema.auxiliary import AUXILIARY_MODELS
from macromind.schema.base import MacroMindObjectBase
from macromind.schema.common import (
    ComparisonBasis,
    ReasoningStep,
    ResolutionCriteria,
    ScenarioBranch,
    TimeReference,
    UnknownValue,
)
from macromind.schema.core import CORE_MODELS

ROOT = Path(__file__).resolve().parents[1]


def build_mapping(contract_root: Path) -> str:
    contract = load_frozen_contract(contract_root)
    definitions = {o.object_name: o for o in contract.core_objects}
    lines = [
        "# Schema Mapping",
        "",
        "Ontology 0.3 / Schema 0.1.0. Generated from the verified frozen contract and model field metadata.",
        "",
        "A = frozen_semantic_requirement; B = validated_auxiliary_contract; C = implementation_extension.",
        "A marks a representation of frozen meaning, not a claim that the frozen contract prescribed this field name or requiredness.",
        "B is sourced from the explicitly non-Core scope, accepted MA.1 auxiliary contract and the execution prompt.",
        "Requiredness, reference encoding, nested shapes and storage types are implementation decisions.",
        'Required nullable fields distinguish missing from null; explicit unknown is `{"state":"unknown"}` or an enum\'s `unknown`.',
        "None means not recorded/not applicable as specified by the field; empty lists mean no references recorded, not proof of absence.",
        "No validation here establishes truth, forecast admission, chronology eligibility, causal validity or evidence sufficiency.",
        "",
        "## Auxiliary reference targets",
        "",
        "Source.version_refs → SourceVersion; Source.segment_refs → SourceSegment; Source.family_ref → SourceFamily.",
        "StructuralProcess.observation_refs → IndicatorObservation; Assessment.information_set_ref → InformationSet.",
        "Claim source_refs → Source; ClaimOccurrence supplies version/segment/origin provenance.",
        "MechanismUsage references Mechanism; AnalystMethodSignal remains distinct from Heuristic; Scenario remains distinct from Forecast.",
        "References are opaque strings. Target existence and semantic consistency are Phase 1.3 responsibilities.",
        "",
    ]
    models = {
        "MacroMindObjectBase": MacroMindObjectBase,
        **CORE_MODELS,
        **AUXILIARY_MODELS,
        **{
            m.__name__: m
            for m in [
                ComparisonBasis,
                ReasoningStep,
                ResolutionCriteria,
                ScenarioBranch,
                TimeReference,
                UnknownValue,
            ]
        },
    }
    for name, model in models.items():
        lines.extend([f"## {name}", "", f"Executable Model: `{model.__module__}.{name}`", ""])
        if name in definitions:
            obj = definitions[name]
            lines.extend(
                [
                    f"Frozen Definition: {obj.core_definition}",
                    "",
                    "Frozen Principle Refs: "
                    + (", ".join(obj.principle_refs) or "none explicitly assigned"),
                    "Known Debt Refs: " + ", ".join(obj.known_nonblocking_debts),
                    "",
                    "Frozen semantic invariants (verbatim):",
                    "",
                    *[f"- {s}" for s in obj.semantic_invariants],
                    "",
                ]
            )
        else:
            lines.extend(
                ["Non-Core/base/nested implementation mapping. No new Core definition.", ""]
            )
        required = [n for n, f in model.model_fields.items() if f.is_required()]
        optional = [n for n, f in model.model_fields.items() if not f.is_required()]
        extensions = [
            n
            for n, f in model.model_fields.items()
            if f.json_schema_extra["field_origin"] == "implementation_extension"
        ]
        refs = [
            n for n in model.model_fields if "ref" in n or n in ("provenance", "premises", "steps")
        ]
        lines.extend(
            [
                "Required Fields: " + ", ".join(required),
                "",
                "Optional Fields: " + (", ".join(optional) or "none"),
                "",
                "Auxiliary References / reference-bearing fields: " + (", ".join(refs) or "none"),
                "",
                "Implementation Extensions: " + ", ".join(extensions),
                "",
                "| Executable field | Origin | Requirement / representation | Source |",
                "| --- | --- | --- | --- |",
            ]
        )
        for field_name, field in model.model_fields.items():
            origin = field.json_schema_extra
            lines.append(
                f"| {field_name} | {origin['field_origin']} | {field.description} | {origin.get('source_ref', 'Phase 1 implementation')} |"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    path = ROOT / "docs/SCHEMA_MAPPING.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_mapping(ROOT.parent / "golden_sample_test/core_ontology/v0.3"),
        encoding="utf-8",
        newline="\n",
    )
