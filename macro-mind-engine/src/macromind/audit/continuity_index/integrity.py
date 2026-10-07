"""Re-read checks against source bytes and trusted context, including provenance."""

from pydantic import ValidationError

from ..ids import canonical_bytes, digest_bytes, semantic_hash
from .identity import result_semantics
from .index import ContinuityIndexer
from .models import ContinuityIndexError, ContinuityIndexResult
from .resolution import require, strict_json


def verify_result(result, verified_input):
    require(
        result.deterministic_hash == semantic_hash(result_semantics(result)),
        "RESULT_SEMANTIC_MISMATCH",
    )
    index = result.relation_index
    require(set(index.relation_by_annotation) == set(result.annotations), "ANNOTATION_COVERAGE")
    for aid, key in index.relation_by_annotation.items():
        require(
            key in index.relations_by_key and aid in index.annotations_by_relation.get(key, []),
            "BROKEN_REVERSE_INDEX",
            aid,
        )
    for mid, row in result.membership_index.memberships_by_id.items():
        require(bool(row["supporting_relations"]), "MISSING_MEMBERSHIP_SUPPORT", mid)
        for key, proof in row["supporting_relations"].items():
            require(
                key in index.relations_by_key
                and not index.relations_by_key[key].membership_blockers,
                "UNQUALIFIED_MEMBERSHIP",
                mid,
            )
            require(bool(proof["annotation_ids"]), "MISSING_ANNOTATION_SUPPORT", mid)
            for aid in proof["annotation_ids"]:
                a = result.annotations.get(aid, {})
                require(
                    a.get("review_status") == "CONFIRMED"
                    and a.get("thread_ref") == row["thread_ref"]
                    and index.relation_by_annotation.get(aid) == key,
                    "INVALID_MEMBERSHIP_PROOF",
                    aid,
                )
    expected = ContinuityIndexer.build(verified_input)
    require(
        canonical_bytes(result.model_dump(mode="json"))
        == canonical_bytes(expected.model_dump(mode="json")),
        "RESULT_SOURCE_MISMATCH",
    )
    return {
        "status": "PASS",
        "annotations": len(result.annotations),
        "memberships": len(result.membership_index.memberships_by_id),
    }


def load_result_bytes(raw, expected_sha256, verified_input):
    require(digest_bytes(raw) == expected_sha256, "RESULT_BYTE_HASH_MISMATCH")
    try:
        result = ContinuityIndexResult.model_validate(strict_json(raw))
    except ValidationError as error:
        raise ContinuityIndexError("RESULT_CONTRACT_ERROR", str(error)) from error
    try:
        verify_result(result, verified_input)
    except (KeyError, TypeError, IndexError) as error:
        raise ContinuityIndexError("RESULT_INTEGRITY_ERROR", str(error)) from error
    return result
