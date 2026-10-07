"""Structural indexes, not ontology objects or new audit occurrences."""

from enum import StrEnum
from typing import Any

from pydantic import Field

from ..ids import canonical_bytes, semantic_hash
from ..models import Contract, RecordType

PATTERN_VERSION = "0.1.0"


class Disposition(StrEnum):
    PATTERN_ELIGIBLE = "PATTERN_ELIGIBLE"
    TRACE_ONLY = "TRACE_ONLY"
    SUMMARY_ONLY = "SUMMARY_ONLY"
    OPAQUE_EXCLUDED = "OPAQUE_EXCLUDED"


class PatternSignature(Contract):
    record_type: RecordType
    component: str
    category: str | None
    rule_id: str | None
    reason_code: str | None
    structured_dimensions: dict[str, Any]
    source_path_shape: str | None
    target_path_shape: str | None

    def pattern_id(self) -> str:
        return "pattern:" + semantic_hash(self.model_dump(mode="json"))


class AuditPattern(Contract):
    pattern_id: str
    signature: PatternSignature
    record_type: RecordType
    component: str
    category: str | None
    rule_id: str | None
    reason_code: str | None
    structured_dimensions: dict[str, Any]
    source_path_shape: str | None
    target_path_shape: str | None
    occurrence_count: int = Field(ge=1)
    artifact_count: int = Field(ge=1)
    occurrence_record_ids: list[str]
    source_artifact_ids: list[str]
    severity_distribution: dict[str, int]
    outcome_distribution: dict[str, int]
    review_required_count: int = Field(ge=0)
    example_record_ids: list[str]


class PatternOccurrenceIndex(Contract):
    by_pattern: dict[str, list[str]]
    by_record: dict[str, str]


class PatternAggregationResult(Contract):
    pattern_version: str = PATTERN_VERSION
    input_normalization_hash: str | None
    patterns: list[AuditPattern]
    pattern_occurrence_index: PatternOccurrenceIndex
    record_dispositions: dict[str, Disposition]
    disposition_counts: dict[str, int]
    disposition_artifact_counts: dict[str, int]
    record_types_by_disposition: dict[str, dict[str, int]]
    eligible_occurrence_count: int
    pattern_count: int
    deterministic_hash: str

    def semantic_payload(self) -> dict[str, Any]:
        # The upstream hash is order-sensitive provenance, not aggregation identity.
        return self.model_dump(
            mode="json", exclude={"deterministic_hash", "input_normalization_hash"}
        )

    def semantic_bytes(self) -> bytes:
        return canonical_bytes(self.semantic_payload())
