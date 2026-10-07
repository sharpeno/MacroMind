"""Compatibility runtime records; never registered ontology objects."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

COMPATIBILITY_ADAPTER_VERSION = "0.1.0"
Operation = Literal[
    "COPY",
    "RENAME",
    "WRAP",
    "FLATTEN",
    "EXPAND_STRUCTURAL",
    "ENUM_MAP",
    "REF_MAP",
    "DEFAULT_UNKNOWN",
    "DROP_NONSEMANTIC",
    "PRESERVE_RAW",
    "QUARANTINE",
    "UNSUPPORTED",
]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DetectionResult(Model):
    family: str
    status: Literal["EXACT", "STRONG", "AMBIGUOUS", "UNKNOWN"]
    evidence: list[str]
    matched_signatures: list[str]
    conflicting_signatures: list[str]
    explicit_version: dict[str, Any]
    shape_hash: str


class AdapterSpec(Model):
    adapter_id: str
    adapter_version: str = COMPATIBILITY_ADAPTER_VERSION
    source_family: str
    target_ontology_version: str = "0.3"
    target_schema_version: str = "0.1.0"
    supported_status: str = "supported_conservatively"
    loss_profile: str
    implementation_module: str


class MappingEntry(Model):
    source_path: str | None
    target_path: str
    operation: Operation
    source_value_hash: str | None
    target_value_hash: str
    semantic_change: Literal[False] = False
    reason: str
    evidence: list[str] = Field(default_factory=list)


class AdaptationLoss(Model):
    loss_id: str
    source_path: str
    category: str
    severity: Literal["INFO", "WARNING", "BLOCKING"]
    description: str
    canonical_effect: str
    preserved_raw: bool = True
    review_required: bool = True


class CompatibilityQuarantineItem(Model):
    source_path: str
    source_object_type: str | None
    raw_payload_hash: str
    raw_payload: Any
    reason_code: str
    message: str
    missing_semantics: list[str]
    candidate_target_type: str | None
    suggested_future_action: str = (
        "Human review or separately versioned compatibility policy; never infer missing facts."
    )


class AdaptationResult(Model):
    source_sha256: str
    source_family: str
    detection_status: str
    adapter_id: str | None
    adapter_version: str = COMPATIBILITY_ADAPTER_VERSION
    target_ontology_version: str = "0.3"
    target_schema_version: str = "0.1.0"
    status: Literal["LOSSLESS", "LOSSY_BUT_SAFE", "PARTIAL", "UNSUPPORTED"]
    canonical_bundle: dict[str, Any]
    quarantined_items: list[CompatibilityQuarantineItem]
    mapping_ledger: list[MappingEntry]
    losses: list[AdaptationLoss]
    unknowns: list[dict[str, Any]]
    warnings: list[str]
    unsupported_fields: list[dict[str, Any]]
    source_object_count: int
    canonical_object_count: int
    quarantined_object_count: int
    deterministic_hash: str
    recommended_validation_mode: Literal["partial_bundle"] = "partial_bundle"
    validator_report_summary: dict[str, Any]
    raw_document: Any
    canonical_reconstruction_forbidden: bool = False
    adaptation_manifest: dict[str, Any] = Field(default_factory=dict)
