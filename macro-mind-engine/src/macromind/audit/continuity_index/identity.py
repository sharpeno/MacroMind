"""Ordered identities and deliberately narrow semantic projections."""

from ..ids import semantic_hash

ANNOTATION_FIELDS = (
    "annotation_id",
    "subject_ref",
    "related_ref",
    "relation_type",
    "reviewer",
    "review_status",
    "thread_ref",
    "resolution_status",
    "evidence_refs",
)


def annotation_projection(annotation):
    return {key: annotation[key] for key in ANNOTATION_FIELDS}


def relation_key(subject, related, relation_type):
    return "relation:" + semantic_hash([subject, related, relation_type])


def membership_id(thread, member):
    return "membership:" + semantic_hash([thread, member])


def result_semantics(result):
    value = result.model_dump(mode="json", exclude={"provenance", "deterministic_hash"})
    value["annotations"] = {
        key: annotation_projection(a) for key, a in value["annotations"].items()
    }
    return value
