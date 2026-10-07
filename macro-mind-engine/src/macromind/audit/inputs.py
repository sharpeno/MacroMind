"""Explicit input capture. No discovery, network access, or source writes."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from pydantic import Field, model_validator

from .ids import canonical_bytes, digest_bytes
from .models import Contract


class InputIntegrityError(ValueError):
    """Hard failure: never emit a partially verified bundle."""


class AuditInputArtifact(Contract):
    artifact_id: str
    artifact_type: str
    path_or_label: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    phase: str
    component: str
    format: str = "json"
    content: Any
    source_metadata: dict[str, Any] = Field(default_factory=dict)
    expected_sha256: str | None = None
    raw_bytes: bytes | None = Field(default=None, exclude=True, repr=False)

    @model_validator(mode="after")
    def validate_integrity(self) -> "AuditInputArtifact":
        self.verify()
        return self

    def verify(self) -> None:
        encoded = canonical_bytes(self.content)
        if self.raw_bytes is not None:
            try:
                captured = canonical_bytes(json.loads(self.raw_bytes))
            except (ValueError, UnicodeError) as exc:
                raise InputIntegrityError("Captured bytes are not valid finite JSON") from exc
            if captured != encoded:
                raise InputIntegrityError("Content differs from captured source bytes")
        actual = digest_bytes(self.raw_bytes if self.raw_bytes is not None else encoded)
        if actual != self.sha256 or (
            self.expected_sha256 is not None and actual != self.expected_sha256
        ):
            raise InputIntegrityError("Source SHA-256 mismatch")

    @classmethod
    def from_content(
        cls,
        content: Any,
        *,
        artifact_type: str,
        phase: str,
        component: str,
        path_or_label: str = "in-memory",
        expected_sha256: str | None = None,
        source_metadata: dict[str, Any] | None = None,
    ) -> "AuditInputArtifact":
        content = deepcopy(content)
        sha = digest_bytes(canonical_bytes(content))
        return cls(
            artifact_id=f"{artifact_type}:{sha}",
            artifact_type=artifact_type,
            path_or_label=path_or_label,
            sha256=sha,
            phase=phase,
            component=component,
            content=content,
            expected_sha256=expected_sha256,
            source_metadata=deepcopy(source_metadata or {}),
        )

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        *,
        artifact_type: str,
        phase: str,
        component: str,
        expected_sha256: str | None = None,
    ) -> "AuditInputArtifact":
        raw = Path(path).read_bytes()
        sha = digest_bytes(raw)
        if expected_sha256 is not None and sha != expected_sha256:
            raise InputIntegrityError("Source SHA-256 mismatch")
        return cls(
            artifact_id=f"{artifact_type}:{sha}",
            artifact_type=artifact_type,
            path_or_label=str(path),
            sha256=sha,
            phase=phase,
            component=component,
            content=json.loads(raw),
            raw_bytes=raw,
            expected_sha256=expected_sha256,
        )


class AuditInputBundle(Contract):
    validation_reports: list[AuditInputArtifact] = Field(default_factory=list)
    adaptation_results: list[AuditInputArtifact] = Field(default_factory=list)
    immutability_reports: list[AuditInputArtifact] = Field(default_factory=list)
    gate_results: list[AuditInputArtifact] = Field(default_factory=list)
    test_reports: list[AuditInputArtifact] = Field(default_factory=list)
    schema_gap_reports: list[AuditInputArtifact] = Field(default_factory=list)
    registry_gap_reports: list[AuditInputArtifact] = Field(default_factory=list)
    debt_overlays: list[AuditInputArtifact] = Field(default_factory=list)
    manifests: list[AuditInputArtifact] = Field(default_factory=list)

    def artifacts(self) -> list[AuditInputArtifact]:
        return [a for name in type(self).model_fields for a in getattr(self, name)]
