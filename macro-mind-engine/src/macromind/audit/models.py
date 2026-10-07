"""Engineering contracts; deliberately independent of the Frozen ontology."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RecordType(StrEnum):
    VALIDATION_FINDING = "VALIDATION_FINDING"
    ADAPTATION_LOSS = "ADAPTATION_LOSS"
    QUARANTINE = "QUARANTINE"
    SCHEMA_GAP = "SCHEMA_GAP"
    REGISTRY_GAP = "REGISTRY_GAP"
    IMMUTABILITY_EVENT = "IMMUTABILITY_EVENT"
    GATE_RESULT = "GATE_RESULT"
    TEST_RESULT = "TEST_RESULT"
    DEBT_STATUS = "DEBT_STATUS"
    MAPPING_EVENT = "MAPPING_EVENT"
    UNKNOWN_ENGINEERING_RECORD = "UNKNOWN_ENGINEERING_RECORD"


class AuditRecord(Contract):
    record_id: str
    record_type: RecordType
    phase: str
    component: str
    category: str | None = None
    severity: str | None = None
    source_severity: str | None = None
    normalized_severity_class: str | None = None
    source_outcome: Any = None
    message: str | None = None
    source_artifact_id: str
    source_artifact_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_pointer: str
    object_ref: Any = None
    source_path: str | None = None
    target_path: str | None = None
    rule_id: str | None = None
    reason_code: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)
    review_required: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedAuditBundle(Contract):
    audit_version: str = "0.1.0"
    input_manifest: list[dict[str, Any]]
    records: list[AuditRecord]
    unsupported_inputs: list[dict[str, Any]]
    normalization_warnings: list[dict[str, Any]]
    record_counts: dict[str, int]
    deterministic_hash: str

    def semantic_payload(self) -> dict[str, Any]:
        data = self.model_dump(mode="json", exclude={"deterministic_hash"})
        # Only envelope location and caller's operational metadata are excluded.
        # Source bytes and their historical fields remain authoritative evidence.
        data["input_manifest"] = [
            {k: v for k, v in item.items() if k not in {"path_or_label", "source_metadata"}}
            for item in data["input_manifest"]
        ]
        return data
