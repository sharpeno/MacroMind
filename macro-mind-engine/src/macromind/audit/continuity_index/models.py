"""Explicit continuity indexing contracts, independent of ontology objects."""

from typing import Any, Literal

from pydantic import Field

from ..models import Contract

DataKind = Literal["REAL", "SYNTHETIC"]


class ContinuityIndexError(ValueError):
    def __init__(self, code: str, location: str = ""):
        self.code, self.location = code, location
        super().__init__(f"{code}: {location}")

    def as_dict(self):
        return {"code": self.code, "location": self.location}


class TrustedContextDescriptor(Contract):
    authority_id: str
    source_version: str
    snapshot_sha256: str
    data_kind: DataKind


class ArtifactDescriptor(Contract):
    artifact_id: str
    sha256: str
    data_kind: DataKind
    path_or_label: str | None = None


class AnnotationSource(Contract):
    annotation_index: int = Field(ge=0)
    source_artifact_id: str
    source_artifact_hash: str
    source_pointer: str
    payload_hash: str
    raw_payload: dict[str, Any]


class ReferenceBinding(Contract):
    ref: str = Field(min_length=1)
    source_artifact_id: str
    source_artifact_sha256: str
    source_pointer: str
    declared_object_type: str | None = None


class ReferenceResolutionSnapshot(Contract):
    snapshot_version: Literal["1.0"] = "1.0"
    authority_id: str
    source_version: str
    references: list[ReferenceBinding]
    source_artifact_hashes: dict[str, str]
    semantic_hash: str

    def semantic_payload(self):
        value = self.model_dump(mode="json", exclude={"semantic_hash"})
        value["references"] = sorted(value["references"], key=lambda x: x["ref"])
        return value


class ContinuityIndexInputBundle(Contract):
    contract_version: Literal["1.0"] = "1.0"
    data_kind: DataKind
    annotation_payloads: list[dict[str, Any]]
    annotation_sources: list[AnnotationSource]
    resolution_snapshot: str
    input_manifest: list[ArtifactDescriptor]
    source_artifact_hashes: dict[str, str]
    deterministic_hash: str


class RelationReviewSummary(Contract):
    status: Literal["CONFLICTED", "CONFIRMED", "REJECTED", "PENDING"]
    annotation_ids_by_status: dict[str, list[str]]
    reviewers_by_annotation: dict[str, str | None]
    conflict: bool


class ThreadAssignmentSummary(Contract):
    status: Literal["NO_ASSERTION", "UNIQUE_ASSERTION", "CONFLICTED"]
    assertions_by_thread: dict[str, list[str]]
    unassigned_annotation_ids: list[str]
    review_status_by_annotation: dict[str, str]
    confirmed_support_by_thread: dict[str, list[str]]
    conflict: bool


class ContinuityRelation(Contract):
    continuity_relation_key: str
    subject_ref: str
    related_ref: str
    relation_type: str
    annotation_ids: list[str]
    review_summary: RelationReviewSummary
    thread_assignment_summary: ThreadAssignmentSummary
    resolution_summary: dict[str, Any]
    membership_blockers: list[str]


class ContinuityRelationIndex(Contract):
    relations_by_key: dict[str, ContinuityRelation]
    relation_by_annotation: dict[str, str]
    annotations_by_relation: dict[str, list[str]]
    relations_by_ref: dict[str, list[str]]
    relations_by_ref_pair: dict[str, dict[str, Any]]
    thread_assertions_by_relation: dict[str, ThreadAssignmentSummary]


class ExplicitThreadMembershipIndex(Contract):
    memberships_by_id: dict[str, dict[str, Any]]
    by_thread: dict[str, list[str]]
    by_ref: dict[str, list[str]]
    by_relation: dict[str, list[str]]


class ContinuityIndexResult(Contract):
    index_version: Literal["1.0"] = "1.0"
    data_kind: DataKind
    annotations: dict[str, dict[str, Any]]
    relation_index: ContinuityRelationIndex
    membership_index: ExplicitThreadMembershipIndex
    conflicts: list[dict[str, Any]]
    counts: dict[str, int]
    provenance: dict[str, Any]
    resolution_context_hash: str
    deterministic_hash: str
