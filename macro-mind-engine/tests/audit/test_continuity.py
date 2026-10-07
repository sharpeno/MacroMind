import pytest
from macromind.audit import ContinuityAnnotation, RelationType


def annotation(**kwargs):
    return ContinuityAnnotation(
        subject_ref="episode:a",
        related_ref="object:b",
        relation_type=kwargs.pop("relation_type", "SAME_ISSUE_CANDIDATE"),
        **kwargs,
    )


def test_default_unreviewed_nullable_thread():
    a = annotation()
    assert a.review_status == "UNREVIEWED"
    assert a.thread_ref is None
    assert a.reviewer is None
    assert a.resolution_status == "UNRESOLVED"


@pytest.mark.parametrize("reviewer", [None, "", "   "])
def test_confirmed_requires_reviewer(reviewer):
    with pytest.raises(ValueError, match="explicit reviewer"):
        annotation(
            review_status="CONFIRMED", reviewer=reviewer, known_refs={"episode:a", "object:b"}
        )


def test_explicit_confirmation():
    a = annotation(
        review_status="CONFIRMED", reviewer="human:alice", known_refs={"episode:a", "object:b"}
    )
    assert a.review_status == "CONFIRMED"
    assert a.resolution_status == "RESOLVED"
    assert a.thread_ref is None


def test_unresolved_not_guessed_or_confirmed():
    a = annotation(
        review_status="CANDIDATE",
        known_refs={"episode:a", "object:similar-b"},
        resolution_status="RESOLVED",
    )
    assert a.resolution_status == "UNRESOLVED"
    assert a.review_status == "CANDIDATE"
    with pytest.raises(ValueError, match="Unresolved"):
        annotation(review_status="CONFIRMED", reviewer="alice", known_refs={"episode:a"})


def test_relation_changes_identity():
    ids = {annotation(relation_type=relation).annotation_id for relation in RelationType}
    assert len(ids) == 8
    assert annotation().annotation_id == annotation().annotation_id


def test_created_at_excluded_from_semantic_hash():
    a = annotation(created_at="2026-01-01T00:00:00Z")
    b = annotation(created_at="2026-09-30T00:00:00Z")
    assert a.annotation_id == b.annotation_id
    assert a.semantic_hash() == b.semantic_hash()


def test_invalid_relation_and_forged_id():
    with pytest.raises(ValueError):
        annotation(relation_type="AUTOMATIC_MATCH")
    with pytest.raises(ValueError):
        annotation(annotation_id="invented")


def test_thread_only_explicit_resolved_reference():
    a = annotation(thread_ref="thread:human", known_refs={"episode:a", "object:b"})
    assert a.thread_ref == "thread:human"
    assert a.resolution_status == "UNRESOLVED"
