"""Internal validator transport/results, never ontology objects or schema exports."""

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

VALIDATOR_VERSION = "0.1.0"


class RuleOutcome(StrEnum):
    PASS = "PASS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INDETERMINATE = "INDETERMINATE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RuntimeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ValidationInput(RuntimeModel):
    objects: list[dict[str, Any]]


class ValidationIssue(RuntimeModel):
    rule_id: str
    rule_name: str
    category: str
    severity: Literal["ERROR", "WARNING", "INFO"]
    outcome: RuleOutcome
    object_ref: str | None
    field_path: str
    message: str
    related_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    review_required: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class RuleExecution(RuntimeModel):
    rule_id: str
    outcome: RuleOutcome
    finding_count: int


class ValidationReport(RuntimeModel):
    validator_version: str = VALIDATOR_VERSION
    ontology_version: str = "0.3"
    schema_version: str = "0.1.0"
    mode: Literal["complete_bundle", "partial_bundle"]
    object_count: int
    rule_count: int
    executed_rule_count: int
    rule_order: list[str]
    rule_results: list[RuleExecution]
    outcome_counts: dict[str, int]
    issues: list[ValidationIssue]
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    indeterminate: list[ValidationIssue]
    not_applicable: list[ValidationIssue]
    deterministic_hash: str
    input_hash: str
    contract_semantic_hash: str
    registry_hash: str
    context_hash: str


class ValidationInputError(ValueError):
    """Malformed transport/context; different from an invalid canonical object."""
