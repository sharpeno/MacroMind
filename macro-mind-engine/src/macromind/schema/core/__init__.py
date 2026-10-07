"""The fourteen executable Core models. Frozen definitions remain authoritative."""

from typing import Literal

from macromind.registry._enums import (
    AnalysisContext,
    ExpressionLevel,
    HeuristicStatus,
    ResolutionStatus,
    VerificationStatus,
)

from ..base import MacroMindObjectBase, Ref, Text, extension, semantic
from ..common import (
    MaybeText,
    ReasoningStep,
    ResolutionCriteria,
    TimeValue,
    UnknownValue,
)


class Source(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Source; ontology_version=0.3."""

    object_type: Literal["Source"] = extension("Registered object discriminator.", "Source")
    title: MaybeText = semantic(
        "Recorded source title", "core_objects.json#Source; core_principles.json"
    )
    locator: MaybeText = semantic(
        "Carrier locator or original URL", "core_objects.json#Source; core_principles.json"
    )
    publisher: MaybeText = semantic(
        "Source publisher identity", "core_objects.json#Source; core_principles.json"
    )
    published_at: TimeValue = semantic(
        "Publication time, not assertion or capture time",
        "core_objects.json#Source; core_principles.json",
    )
    version_refs: list[Ref] = semantic(
        "Recorded source versions", "core_objects.json#Source; core_principles.json"
    )
    segment_refs: list[Ref] = semantic(
        "Source segments", "core_objects.json#Source; core_principles.json"
    )
    family_ref: Ref | None = semantic(
        "Origin family; no inferred independent support",
        "core_objects.json#Source; core_principles.json",
    )


class Claim(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Claim; ontology_version=0.3."""

    object_type: Literal["Claim"] = extension("Registered object discriminator.", "Claim")
    statement: Text = semantic(
        "Asserted proposition", "core_objects.json#Claim; core_principles.json"
    )
    claimant: MaybeText = semantic(
        "Speaker or claimant attribution", "core_objects.json#Claim; core_principles.json"
    )
    asserted_at: TimeValue = semantic(
        "Assertion time, preserved independently of publication",
        "core_objects.json#Claim; core_principles.json",
    )
    reference_time: TimeValue = semantic(
        "Time the proposition concerns", "core_objects.json#Claim; core_principles.json"
    )
    population: MaybeText = semantic(
        "Population the proposition quantifies over",
        "core_objects.json#Claim; core_principles.json",
    )
    quantifier: MaybeText = semantic(
        "Original quantifier", "core_objects.json#Claim; core_principles.json"
    )
    modal_strength: MaybeText = semantic(
        "Original modality, without invented strength",
        "core_objects.json#Claim; core_principles.json",
    )
    scope: MaybeText = semantic(
        "Scope of assertion", "core_objects.json#Claim; core_principles.json"
    )
    source_refs: list[Ref] = semantic(
        "Source attribution", "core_objects.json#Claim; core_principles.json"
    )
    reasoner_id: Ref | None = semantic(
        "Reasoner attribution", "core_objects.json#Claim; core_principles.json"
    )
    analysis_context: AnalysisContext = semantic(
        "Analysis context", "core_objects.json#Claim; core_principles.json"
    )
    annotation_observer: Ref | None = semantic(
        "Observer recording the claim", "core_objects.json#Claim; core_principles.json"
    )


class Event(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Event; ontology_version=0.3."""

    object_type: Literal["Event"] = extension("Registered object discriminator.", "Event")
    description: Text = semantic(
        "Time-bounded state change", "core_objects.json#Event; core_principles.json"
    )
    announced_at: TimeValue = semantic(
        "Announcement time", "core_objects.json#Event; core_principles.json"
    )
    decided_at: TimeValue = semantic(
        "Decision time", "core_objects.json#Event; core_principles.json"
    )
    scheduled_at: TimeValue = semantic(
        "Scheduled time", "core_objects.json#Event; core_principles.json"
    )
    effective_at: TimeValue = semantic(
        "Effective time", "core_objects.json#Event; core_principles.json"
    )
    occurred_at: TimeValue = semantic(
        "Occurrence time", "core_objects.json#Event; core_principles.json"
    )
    occurrence_status: MaybeText = semantic(
        "Recorded occurrence status, not inferred from a Claim",
        "core_objects.json#Event; core_principles.json",
    )
    evidence_refs: list[Ref] = semantic(
        "Occurrence evidence", "core_objects.json#Event; core_principles.json"
    )
    actor_refs: list[Ref] = semantic(
        "Actors involved", "core_objects.json#Event; core_principles.json"
    )
    policy_refs: list[Ref] = semantic(
        "Related policy states", "core_objects.json#Event; core_principles.json"
    )
    subtype: MaybeText = extension("Implementation extension: event subtype; not a new Core")


class StructuralProcess(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#StructuralProcess; ontology_version=0.3."""

    object_type: Literal["StructuralProcess"] = extension(
        "Registered object discriminator.", "StructuralProcess"
    )
    description: Text = semantic(
        "Persistent real structural change",
        "core_objects.json#StructuralProcess; core_principles.json",
    )
    period: TimeValue = semantic(
        "Evidence period", "core_objects.json#StructuralProcess; core_principles.json"
    )
    event_refs: list[Ref] = semantic(
        "Supporting events; no invented minimum count",
        "core_objects.json#StructuralProcess; core_principles.json",
    )
    observation_refs: list[Ref] = semantic(
        "Cross-period observations", "core_objects.json#StructuralProcess; core_principles.json"
    )
    policy_refs: list[Ref] = semantic(
        "Supporting policy states", "core_objects.json#StructuralProcess; core_principles.json"
    )
    evidence_refs: list[Ref] = semantic(
        "Supporting evidence; sufficiency deferred",
        "core_objects.json#StructuralProcess; core_principles.json",
    )


class Actor(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Actor; ontology_version=0.3."""

    object_type: Literal["Actor"] = extension("Registered object discriminator.", "Actor")
    display_name: MaybeText = semantic(
        "Display name distinct from identity", "core_objects.json#Actor; core_principles.json"
    )
    identity_evidence_refs: list[Ref] = semantic(
        "Evidence for acting or decision-making identity",
        "core_objects.json#Actor; core_principles.json",
    )
    aliases: list[Text] = extension(
        "Implementation extension: recorded aliases without automatic merge"
    )
    location: MaybeText = semantic(
        "Geography distinct from Actor identity", "core_objects.json#Actor; core_principles.json"
    )
    roles: list[Text] = semantic(
        "Narrative roles distinct from identity", "core_objects.json#Actor; core_principles.json"
    )


class Indicator(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Indicator; ontology_version=0.3."""

    object_type: Literal["Indicator"] = extension("Registered object discriminator.", "Indicator")
    name: Text = semantic(
        "Reusable variable name", "core_objects.json#Indicator; core_principles.json"
    )
    definition: Text = semantic(
        "Variable definition", "core_objects.json#Indicator; core_principles.json"
    )
    measurement_scope: MaybeText = semantic(
        "Measurement population and basis", "core_objects.json#Indicator; core_principles.json"
    )
    unit: MaybeText = semantic(
        "Defined measurement unit", "core_objects.json#Indicator; core_principles.json"
    )
    source_refs: list[Ref] = semantic(
        "Definition sources", "core_objects.json#Indicator; core_principles.json"
    )


class Policy(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Policy; ontology_version=0.3."""

    object_type: Literal["Policy"] = extension("Registered object discriminator.", "Policy")
    description: Text = semantic(
        "Persistent institutional arrangement", "core_objects.json#Policy; core_principles.json"
    )
    effective_period: TimeValue = semantic(
        "Period of validity", "core_objects.json#Policy; core_principles.json"
    )
    actor_refs: list[Ref] = semantic(
        "Responsible actors", "core_objects.json#Policy; core_principles.json"
    )
    event_refs: list[Ref] = semantic(
        "Separate announcement, implementation or adjustment events",
        "core_objects.json#Policy; core_principles.json",
    )
    source_refs: list[Ref] = semantic(
        "Policy evidence", "core_objects.json#Policy; core_principles.json"
    )


class Mechanism(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Mechanism; ontology_version=0.3."""

    object_type: Literal["Mechanism"] = extension("Registered object discriminator.", "Mechanism")
    statement: Text = semantic(
        "Reusable causal structure", "core_objects.json#Mechanism; core_principles.json"
    )
    causal_structure: MaybeText = semantic(
        "Causal relationships", "core_objects.json#Mechanism; core_principles.json"
    )
    applicability_conditions: MaybeText = semantic(
        "Conditions for reuse", "core_objects.json#Mechanism; core_principles.json"
    )
    domain_scope: MaybeText = semantic(
        "Applicable domain", "core_objects.json#Mechanism; core_principles.json"
    )
    reasoner_id: Ref | None = semantic(
        "Mechanism author; usage analyst is not automatically author",
        "core_objects.json#Mechanism; core_principles.json",
    )
    analysis_context: AnalysisContext = semantic(
        "Context of mechanism attribution", "core_objects.json#Mechanism; core_principles.json"
    )
    annotation_observer: Ref | None = semantic(
        "Observer recording attribution", "core_objects.json#Mechanism; core_principles.json"
    )
    source_refs: list[Ref] = semantic(
        "Sources for the mechanism", "core_objects.json#Mechanism; core_principles.json"
    )


class Argument(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Argument; ontology_version=0.3."""

    object_type: Literal["Argument"] = extension("Registered object discriminator.", "Argument")
    premises: list[Ref] = semantic(
        "Premise references", "core_objects.json#Argument; core_principles.json"
    )
    steps: list[ReasoningStep] = semantic(
        "Attributed inference graph edges", "core_objects.json#Argument; core_principles.json"
    )
    intermediate_conclusions: list[Ref] = semantic(
        "Intermediate conclusion nodes", "core_objects.json#Argument; core_principles.json"
    )
    final_conclusion: Ref | None = semantic(
        "Final conclusion reference", "core_objects.json#Argument; core_principles.json"
    )
    expression_level: ExpressionLevel = semantic(
        "Recorded expression level", "core_objects.json#Argument; core_principles.json"
    )
    reasoner_id: Ref | None = semantic(
        "Argument reasoner", "core_objects.json#Argument; core_principles.json"
    )
    analysis_context: AnalysisContext = semantic(
        "Reconstruction versus diagnostic context",
        "core_objects.json#Argument; core_principles.json",
    )
    inferential_distance: MaybeText = semantic(
        "Recorded distance and counting basis; edge count is not longest path",
        "core_objects.json#Argument; core_principles.json",
    )
    creator_shortcuts: list[Text] = semantic(
        "Creator shortcuts retained as expressed",
        "core_objects.json#Argument; core_principles.json",
    )
    most_fragile_step: list[Ref] | UnknownValue | None = semantic(
        "Local step refs or paths; unknown allowed",
        "core_objects.json#Argument; core_principles.json",
    )
    source_refs: list[Ref] = semantic(
        "Argument sources", "core_objects.json#Argument; core_principles.json"
    )


class Thesis(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Thesis; ontology_version=0.3."""

    object_type: Literal["Thesis"] = extension("Registered object discriminator.", "Thesis")
    statement: Text = semantic(
        "Persistent explanatory or structural judgment",
        "core_objects.json#Thesis; core_principles.json",
    )
    scope: MaybeText = semantic(
        "Scope of structural explanation", "core_objects.json#Thesis; core_principles.json"
    )
    argument_refs: list[Ref] = semantic(
        "Supporting arguments", "core_objects.json#Thesis; core_principles.json"
    )
    event_refs: list[Ref] = semantic(
        "Events explained", "core_objects.json#Thesis; core_principles.json"
    )
    process_refs: list[Ref] = semantic(
        "Processes explained", "core_objects.json#Thesis; core_principles.json"
    )
    indicator_refs: list[Ref] = semantic(
        "Indicator combination explained", "core_objects.json#Thesis; core_principles.json"
    )
    supporting_evidence_refs: list[Ref] = semantic(
        "Supporting evidence", "core_objects.json#Thesis; core_principles.json"
    )
    counterevidence_refs: list[Ref] = semantic(
        "Interface for later counterevidence", "core_objects.json#Thesis; core_principles.json"
    )


class Forecast(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Forecast; ontology_version=0.3."""

    object_type: Literal["Forecast"] = extension("Registered object discriminator.", "Forecast")
    claim_ref: Ref = semantic(
        "Subject's future judgment expressed by Claim",
        "core_objects.json#Forecast; core_principles.json",
    )
    knowledge_cutoff: TimeValue = semantic(
        "Knowledge cutoff, not evaluation time", "core_objects.json#Forecast; core_principles.json"
    )
    prediction_window: TimeValue = semantic(
        "Prediction window; unknown allowed", "core_objects.json#Forecast; core_principles.json"
    )
    modal_strength: MaybeText = semantic(
        "Original modality", "core_objects.json#Forecast; core_principles.json"
    )
    resolution_criteria: ResolutionCriteria | UnknownValue | None = semantic(
        "Criteria and origin; unknown allowed", "core_objects.json#Forecast; core_principles.json"
    )
    claimant: MaybeText = semantic(
        "Subject assuming the judgment", "core_objects.json#Forecast; core_principles.json"
    )
    conditions: MaybeText = semantic(
        "Conditions of judgment", "core_objects.json#Forecast; core_principles.json"
    )
    branch_selection: MaybeText = semantic(
        "Recorded branch selection without inferring endorsement",
        "core_objects.json#Forecast; core_principles.json",
    )
    resolution_status: ResolutionStatus = semantic(
        "Recorded resolution status", "core_objects.json#Forecast; core_principles.json"
    )
    source_refs: list[Ref] = semantic(
        "Original judgment sources", "core_objects.json#Forecast; core_principles.json"
    )


class Contradiction(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Contradiction; ontology_version=0.3."""

    object_type: Literal["Contradiction"] = extension(
        "Registered object discriminator.", "Contradiction"
    )
    description: Text = semantic(
        "Persistent structural tension, not a claim disagreement edge",
        "core_objects.json#Contradiction; core_principles.json",
    )
    period: TimeValue = semantic(
        "Persistence across time", "core_objects.json#Contradiction; core_principles.json"
    )
    conflicting_goals: list[Text] = semantic(
        "Recorded competing goals", "core_objects.json#Contradiction; core_principles.json"
    )
    constraints: list[Text] = semantic(
        "Recorded competing constraints", "core_objects.json#Contradiction; core_principles.json"
    )
    event_refs: list[Ref] = semantic(
        "Supporting events", "core_objects.json#Contradiction; core_principles.json"
    )
    thesis_refs: list[Ref] = semantic(
        "Supporting theses", "core_objects.json#Contradiction; core_principles.json"
    )
    interactions: list[Text] = semantic(
        "Recorded interactions supporting the tension",
        "core_objects.json#Contradiction; core_principles.json",
    )


class Assessment(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Assessment; ontology_version=0.3."""

    object_type: Literal["Assessment"] = extension("Registered object discriminator.", "Assessment")
    observer: Ref | None = semantic(
        "Observer making this assessment", "core_objects.json#Assessment; core_principles.json"
    )
    target_ref: Ref = semantic(
        "Target evaluated", "core_objects.json#Assessment; core_principles.json"
    )
    assessment_kind: Text = semantic(
        "Kind of assessment, independent of truth",
        "core_objects.json#Assessment; core_principles.json",
    )
    criteria: MaybeText = semantic(
        "Evaluation criteria", "core_objects.json#Assessment; core_principles.json"
    )
    information_set_ref: Ref | None = semantic(
        "Information available to observer", "core_objects.json#Assessment; core_principles.json"
    )
    assessment_time: TimeValue = semantic(
        "Evaluation time", "core_objects.json#Assessment; core_principles.json"
    )
    verification_status: VerificationStatus = semantic(
        "Attributed verification judgment", "core_objects.json#Assessment; core_principles.json"
    )
    detail: MaybeText = semantic(
        "Assessment detail, never written back to reality",
        "core_objects.json#Assessment; core_principles.json",
    )


class Heuristic(MacroMindObjectBase):
    """Frozen object definition: core_objects.json#Heuristic; ontology_version=0.3."""

    object_type: Literal["Heuristic"] = extension("Registered object discriminator.", "Heuristic")
    statement: Text = semantic(
        "Reusable analytical action or check", "core_objects.json#Heuristic; core_principles.json"
    )
    scope: MaybeText = semantic(
        "Applicability scope", "core_objects.json#Heuristic; core_principles.json"
    )
    trigger_conditions: list[Text] = semantic(
        "Conditions triggering the action", "core_objects.json#Heuristic; core_principles.json"
    )
    required_inputs: list[Text] = semantic(
        "Inputs needed", "core_objects.json#Heuristic; core_principles.json"
    )
    analytical_action: MaybeText = semantic(
        "Action to perform", "core_objects.json#Heuristic; core_principles.json"
    )
    allowed_outputs: list[Text] = semantic(
        "Permitted results", "core_objects.json#Heuristic; core_principles.json"
    )
    forbidden_leaps: list[Text] = semantic(
        "Unsupported leaps to avoid", "core_objects.json#Heuristic; core_principles.json"
    )
    counterexamples: list[Ref] = semantic(
        "Counterexample evidence", "core_objects.json#Heuristic; core_principles.json"
    )
    failure_conditions: list[Text] = semantic(
        "Failure conditions", "core_objects.json#Heuristic; core_principles.json"
    )
    status: HeuristicStatus = semantic(
        "Recorded candidate status; no Skill promotion",
        "core_objects.json#Heuristic; core_principles.json",
    )
    provenance: list[Ref] = semantic(
        "Evidence and attribution", "core_objects.json#Heuristic; core_principles.json"
    )


CORE_MODELS = {
    cls.__name__: cls
    for cls in (
        Source,
        Claim,
        Event,
        StructuralProcess,
        Actor,
        Indicator,
        Policy,
        Mechanism,
        Argument,
        Thesis,
        Forecast,
        Contradiction,
        Assessment,
        Heuristic,
    )
}
