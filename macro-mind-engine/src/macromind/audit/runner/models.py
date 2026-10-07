"""Versioned orchestration contracts; not ontology objects."""

from typing import Literal

from pydantic import Field

from ...validation import ValidationContext
from ..models import Contract

VERSION = "1.0"
STAGES = (
    "capture",
    "foundation",
    "adaptation",
    "validation",
    "normalization",
    "patterns",
    "continuity",
    "report",
    "persistence",
)


class RunnerError(ValueError):
    def __init__(self, code, location="", exit_code=2):
        self.code, self.location, self.exit_code = code, str(location), exit_code
        super().__init__(f"{code}: {location}")


class SourceSpec(Contract):
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_type: str
    phase: str
    component: str
    data_kind: Literal["REAL", "SYNTHETIC"]


class FoundationSpec(Contract):
    path: str
    tree_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ContinuitySpec(Contract):
    bundle: SourceSpec
    artifacts: dict[str, SourceSpec]


class AuditRunRequest(Contract):
    request_version: Literal["1.0"] = "1.0"
    policy_version: Literal["1.0"] = "1.0"
    ontology_version: Literal["0.3"] = "0.3"
    schema_version: Literal["0.1.0"] = "0.1.0"
    data_kind: Literal["REAL", "SYNTHETIC"]
    input_mode: Literal["CANONICAL", "LEGACY", "ENGINEERING_REPORTS"]
    sources: list[SourceSpec]
    contract: FoundationSpec
    registry: FoundationSpec
    validation_context: ValidationContext = Field(default_factory=ValidationContext)
    continuity: ContinuitySpec | None = None


class StageResult(Contract):
    status: Literal["RUNNING", "COMPLETED", "FAILED", "NOT_APPLICABLE", "NOT_RUN"] = "NOT_RUN"
    reason: str | None = None


class RunSummary(Contract):
    execution_status: Literal["RUNNING", "COMPLETED", "FAILED", "INTERRUPTED"]
    findings_status: Literal[
        "NO_BLOCKING_FINDINGS", "BLOCKING_FINDINGS", "INDETERMINATE", "NOT_ASSESSED"
    ]
    coverage: dict
    counts: dict
    exit_code: int
