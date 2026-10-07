"""Non-Core objects; provenance and structure only, without semantic promotion."""

from typing import Literal

from macromind.registry._enums import (
    AnalysisContext,
    ExpressionLevel,
    FailureType,
    RecognitionStage,
    RecurrenceMatch,
    RecurrenceStatus,
    ReviewStatus,
    SemanticRole,
    SignalType,
    Transferability,
    ValueKind,
)

from ..base import MacroMindObjectBase, Ref, Text, auxiliary, extension
from ..common import (
    ComparisonBasis,
    MaybeText,
    NumberValue,
    ScenarioBranch,
    TimeValue,
)


class SourceVersion(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["SourceVersion"] = extension(
        "Registered object discriminator.", "SourceVersion"
    )
    source_ref: Ref = auxiliary(
        "Versioned carrier", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    version_label: MaybeText = auxiliary(
        "Recorded version label", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    content_time: TimeValue = auxiliary(
        "Content chronology", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    published_at: TimeValue = auxiliary(
        "Publication time", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    captured_at: TimeValue = auxiliary(
        "Capture time", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    content_sha256: MaybeText = auxiliary(
        "Hash of captured bytes, unknown if no snapshot",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    revision_status: MaybeText = auxiliary(
        "Historical edits unknown unless evidenced",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_refs: list[Ref] = auxiliary(
        "Version provenance", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )


class SourceSegment(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["SourceSegment"] = extension(
        "Registered object discriminator.", "SourceSegment"
    )
    source_ref: Ref = auxiliary(
        "Parent source", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    source_version_ref: Ref | None = auxiliary(
        "Actual source version if recorded",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    locator: MaybeText = auxiliary(
        "Page, offset or entry locator",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    text: MaybeText = auxiliary(
        "Original segment text", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    content_time: TimeValue = auxiliary(
        "Segment-specific time, independent of page date",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )


class SourceFamily(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["SourceFamily"] = extension(
        "Registered object discriminator.", "SourceFamily"
    )
    description: MaybeText = auxiliary(
        "Common proposition origin, not blanket source independence",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_refs: list[Ref] = auxiliary(
        "Sources sharing evidenced origin",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    evidence_refs: list[Ref] = auxiliary(
        "Origin matching evidence",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )


class ClaimOccurrence(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["ClaimOccurrence"] = extension(
        "Registered object discriminator.", "ClaimOccurrence"
    )
    claim_ref: Ref = auxiliary(
        "Canonical proposition", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    source_segment_ref: Ref = auxiliary(
        "Specific occurrence location",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_version_ref: Ref | None = auxiliary(
        "Recorded source version",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    origin_family_ref: Ref | None = auxiliary(
        "Proposition origin family",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    asserted_at: TimeValue = auxiliary(
        "Occurrence assertion time",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )


class TranscriptCorrection(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["TranscriptCorrection"] = extension(
        "Registered object discriminator.", "TranscriptCorrection"
    )
    source_segment_ref: Ref = auxiliary(
        "Original transcript segment",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    original_text: Text = auxiliary(
        "Unmodified original text",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    corrected_text: Text = auxiliary(
        "Attributed correction", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    reason: MaybeText = auxiliary(
        "Correction evidence", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    observer: Ref | None = auxiliary(
        "Correction author", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    source_refs: list[Ref] = auxiliary(
        "Supporting evidence", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )


class IndicatorObservation(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["IndicatorObservation"] = extension(
        "Registered object discriminator.", "IndicatorObservation"
    )
    indicator_ref: Ref = auxiliary(
        "Reusable indicator definition",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    value: NumberValue = auxiliary(
        "Recorded number or explicit unknown",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    unit: MaybeText = auxiliary(
        "Recorded unit without conversion",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    period: TimeValue = auxiliary(
        "Observation period", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    value_kind: ValueKind = auxiliary(
        "Target/design/guidance/observed category",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    comparison_basis: ComparisonBasis = auxiliary(
        "Reported comparison structure",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    semantic_role: SemanticRole = auxiliary(
        "Economic role", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    semantic_role_detail: MaybeText = auxiliary(
        "Other or legacy specialized role",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    recognition_stage: RecognitionStage = auxiliary(
        "Recorded recognition stage",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    storage_role: MaybeText = auxiliary(
        "Recorded storage role; unknown retained",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_refs: list[Ref] = auxiliary(
        "Observation sources", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )


class InformationSet(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["InformationSet"] = extension(
        "Registered object discriminator.", "InformationSet"
    )
    knowledge_cutoff: TimeValue = auxiliary(
        "Information eligibility boundary",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    purpose: AnalysisContext = auxiliary(
        "Purpose of information set",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_version_refs: list[Ref] = auxiliary(
        "Specific source versions",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    content_refs: list[Ref] = auxiliary(
        "Available content refs", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    observer: Ref | None = auxiliary(
        "Information-set observer",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )


class ExpectationSnapshot(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["ExpectationSnapshot"] = extension(
        "Registered object discriminator.", "ExpectationSnapshot"
    )
    population: MaybeText = auxiliary(
        "Population holding the expectation",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    reference_time: TimeValue = auxiliary(
        "Expectation reference time",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    captured_at: TimeValue = auxiliary(
        "Snapshot time", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    statement: MaybeText = auxiliary(
        "Expectation as recorded",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_refs: list[Ref] = auxiliary(
        "Evidence sources", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )


class Scenario(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["Scenario"] = extension("Registered object discriminator.", "Scenario")
    claim_refs: list[Ref] = auxiliary(
        "Original conditional statements",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    branches: list[ScenarioBranch] = auxiliary(
        "Possible branches, without forecast inheritance",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_refs: list[Ref] = auxiliary(
        "Scenario provenance", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    reasoner_id: Ref | None = auxiliary(
        "Scenario reasoner", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )


class ReviewQueueItem(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["ReviewQueueItem"] = extension(
        "Registered object discriminator.", "ReviewQueueItem"
    )
    target_ref: Ref = auxiliary(
        "Target needing review", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    field_path: MaybeText = extension("Field or nested path needing review")
    reason: Text = auxiliary(
        "Reason for review", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    status: ReviewStatus = extension("Recorded review state; never waives schema validity")
    observer: Ref | None = auxiliary(
        "Reviewer attribution", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    decision_origin: MaybeText = auxiliary(
        "Decision source", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    resolved_at: TimeValue = auxiliary(
        "Resolution time", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )


class AnalystMethodSignal(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["AnalystMethodSignal"] = extension(
        "Registered object discriminator.", "AnalystMethodSignal"
    )
    analyst_id: Ref | None = auxiliary(
        "Analyst being observed", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    signal_type: SignalType = auxiliary(
        "Type of local behavior", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    statement: Text = auxiliary(
        "Observed local behavior",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_segment_refs: list[Ref] = auxiliary(
        "Original expression evidence",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    argument_refs: list[Ref] = auxiliary(
        "Related arguments", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    claim_refs: list[Ref] = auxiliary(
        "Related claims", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    domain: MaybeText = auxiliary(
        "Recorded domain", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    expression_level: ExpressionLevel = auxiliary(
        "Expression strength", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    transferability: Transferability = auxiliary(
        "Recorded transferability",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    recurrence_status: RecurrenceStatus = auxiliary(
        "Recorded recurrence, no counting or chronology inference",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    recurrence_match: RecurrenceMatch = auxiliary(
        "Precision of match, separate from frequency",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    matched_prior_signal_refs: list[Ref] = auxiliary(
        "Recorded prior matches; no eligibility assertion",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    matched_scope: MaybeText = auxiliary(
        "Exact sub-operation matched",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    recurrence_evidence: list[Ref] = auxiliary(
        "Evidence supporting recorded recurrence",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    reasoner_id: Ref | None = auxiliary(
        "Reasoner attribution", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    analysis_context: AnalysisContext = auxiliary(
        "Analysis context", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    annotation_observer: Ref | None = auxiliary(
        "Annotator distinct from observed reasoner",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    observed_reasoner_id: Ref | None = auxiliary(
        "Observed reasoner for failure analysis",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    observed_action: MaybeText = auxiliary(
        "Action being assessed", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    failure_assessment: MaybeText = auxiliary(
        "Observer's failure assessment",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    failure_type: list[FailureType] | None = auxiliary(
        "Failure categories, None if not applicable",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    assessment_confidence: NumberValue = auxiliary(
        "Confidence in failure assessment, not original assertion confidence",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )


class MechanismUsage(MacroMindObjectBase):
    """Auxiliary mapping: frozen non-Core scope and validated MA.1; ontology_version=0.3."""

    object_type: Literal["MechanismUsage"] = extension(
        "Registered object discriminator.", "MechanismUsage"
    )
    mechanism_ref: Ref = auxiliary(
        "Shared mechanism used", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    analyst_id: Ref | None = auxiliary(
        "Using analyst", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    reasoner_id: Ref | None = auxiliary(
        "Reasoner of this usage only",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    usage_context: MaybeText = auxiliary(
        "Usage context", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    expression_level: ExpressionLevel = auxiliary(
        "Recorded usage expression",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    source_refs: list[Ref] = auxiliary(
        "Usage evidence", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    argument_refs: list[Ref] = auxiliary(
        "Arguments using mechanism",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )
    domain_scope: MaybeText = auxiliary(
        "Domain of use", "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract"
    )
    confidence: NumberValue = auxiliary(
        "Recorded confidence, no inference",
        "Frozen auxiliary scope/P13/P15; MA.1 accepted auxiliary contract",
    )


AUXILIARY_MODELS = {
    cls.__name__: cls
    for cls in (
        SourceVersion,
        SourceSegment,
        SourceFamily,
        ClaimOccurrence,
        TranscriptCorrection,
        IndicatorObservation,
        InformationSet,
        ExpectationSnapshot,
        Scenario,
        ReviewQueueItem,
        AnalystMethodSignal,
        MechanismUsage,
    )
}
