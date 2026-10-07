"""Explicit human annotations only; no similarity analysis or thread creation."""

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, model_validator

from .ids import semantic_hash
from .models import Contract


class RelationType(StrEnum):
    SAME_ISSUE_CANDIDATE = "SAME_ISSUE_CANDIDATE"
    NEW_EVIDENCE = "NEW_EVIDENCE"
    REPEAT_EVIDENCE = "REPEAT_EVIDENCE"
    COUNTER_EVIDENCE = "COUNTER_EVIDENCE"
    THESIS_REFINEMENT = "THESIS_REFINEMENT"
    FORECAST_UPDATE = "FORECAST_UPDATE"
    METHOD_REUSE = "METHOD_REUSE"
    UNCERTAIN_RELATION = "UNCERTAIN_RELATION"


class ReviewStatus(StrEnum):
    UNREVIEWED = "UNREVIEWED"
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class ContinuityAnnotation(Contract):
    annotation_id: str = ""
    subject_ref: str = Field(min_length=1)
    related_ref: str = Field(min_length=1)
    thread_ref: str | None = None
    relation_type: RelationType
    review_status: ReviewStatus = ReviewStatus.UNREVIEWED
    reviewer: str | None = None
    review_notes: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    resolution_status: Literal["RESOLVED", "UNRESOLVED"] = "UNRESOLVED"
    # Caller supplies real, already-resolved references, never inferred from text.
    known_refs: frozenset[str] = Field(default_factory=frozenset, exclude=True)

    @model_validator(mode="after")
    def validate_annotation(self) -> "ContinuityAnnotation":
        refs = [self.subject_ref, self.related_ref]
        if self.thread_ref is not None:
            refs.append(self.thread_ref)
        resolved = all(ref in self.known_refs for ref in refs)
        object.__setattr__(self, "resolution_status", "RESOLVED" if resolved else "UNRESOLVED")
        if self.review_status == ReviewStatus.CONFIRMED:
            if not self.reviewer or not self.reviewer.strip():
                raise ValueError("Human confirmation requires an explicit reviewer")
            if not resolved:
                raise ValueError("Unresolved references cannot be confirmed")
        identity = "continuity:" + semantic_hash(
            [self.subject_ref, self.related_ref, self.relation_type.value, self.reviewer]
        )
        if self.annotation_id and self.annotation_id != identity:
            raise ValueError("Annotation identity does not match its semantic fields")
        object.__setattr__(self, "annotation_id", identity)
        return self

    def semantic_hash(self) -> str:
        return semantic_hash(self.model_dump(mode="json", exclude={"created_at"}))
