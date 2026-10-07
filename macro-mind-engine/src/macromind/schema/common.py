"""Nested value structures, not additional Core or Auxiliary object types."""

from datetime import datetime
from typing import Literal

from macromind.registry._enums import AnalysisContext, ComparisonType, ExpressionLevel

from .base import Ref, SchemaModel, Text, auxiliary, extension, semantic


class UnknownValue(SchemaModel):
    state: Literal["unknown"] = extension("Explicit known-but-undetermined value.", "unknown")


class TimeReference(SchemaModel):
    text: Text = extension("Original temporal expression; no inferred exact date.")
    start: datetime | None = extension("Recorded start, if known.", None)
    end: datetime | None = extension("Recorded end, if known.", None)
    source_ref: Ref | None = extension("Evidence for this temporal expression.", None)


MaybeText = Text | UnknownValue | None
TimeValue = TimeReference | UnknownValue | None
NumberValue = float | UnknownValue | None


class ComparisonBasis(SchemaModel):
    comparison_type: ComparisonType = auxiliary(
        "Reported comparison category, including unknown.", "MA.1 comparison_basis"
    )
    baseline_value: NumberValue = auxiliary(
        "Reported baseline; never calculated.", "MA.1 comparison_basis"
    )
    baseline_period: TimeValue = auxiliary(
        "Baseline period independent of observation period.", "MA.1 comparison_basis"
    )
    baseline_source_ref: Ref | None = auxiliary(
        "Baseline provenance, None when unrecorded.", "MA.1 comparison_basis"
    )
    delta_value: NumberValue = auxiliary(
        "Reported delta, not inferred from values.", "MA.1 comparison_basis"
    )
    delta_unit: MaybeText = auxiliary(
        "Preserve percent versus percentage point or original ambiguity.", "MA.1 comparison_basis"
    )


class ReasoningStep(SchemaModel):
    id: Ref = extension("Stable step identifier within an Argument.")
    premises: list[Ref] = semantic("Premise node references.", "Argument/P08")
    conclusion_ref: Ref | None = semantic(
        "Conclusion node reference; None when unrecorded.", "Argument/P08"
    )
    statement: MaybeText = semantic(
        "Recorded inference, without judging its validity.", "Argument/P08"
    )
    expression_level: ExpressionLevel = semantic(
        "Attribution of expression, separate from truth.", "P15/P16"
    )
    reasoner_id: Ref | None = semantic(
        "Reasoner of this specific edge; never inherited by inference.", "P15"
    )
    analysis_context: AnalysisContext = semantic("Context of this edge.", "P15")
    source_refs: list[Ref] = semantic("Evidence for this edge.", "P01/P15")


class ResolutionCriteria(SchemaModel):
    description: MaybeText = semantic(
        "Original or explicitly attributed resolution criterion.", "Forecast/P13"
    )
    reasoner_id: Ref | None = semantic(
        "Criterion originator; creator/model/human kept distinct.", "P15"
    )
    analysis_context: AnalysisContext = semantic("Criterion origin context.", "P15")
    set_at: TimeValue = semantic("Time criterion was set.", "P13")
    approved_at: TimeValue = semantic("Approval time, independent of evaluation time.", "P13")
    evaluation_time: TimeValue = semantic("Actual evaluation time.", "P13")
    scoring_permitted: bool | UnknownValue | None = semantic(
        "Recorded scoring permission; no automatic approval.", "Forecast temporal contract"
    )


class ScenarioBranch(SchemaModel):
    id: Ref = extension("Local branch identifier.")
    condition: MaybeText = auxiliary("Branch condition, with no implied endorsement.", "B09")
    outcome: MaybeText = auxiliary("Possible consequence, not a forecast commitment.", "B09")
    child_branch_refs: list[Ref] = extension("Optional branch-tree links.", [])
