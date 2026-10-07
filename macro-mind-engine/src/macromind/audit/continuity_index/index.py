"""Explicit, local aggregation: no similarity, votes, or transitive closure."""

from collections import defaultdict

from ..ids import canonical_bytes, digest_bytes, semantic_hash
from .identity import membership_id, relation_key, result_semantics
from .inputs import decode
from .models import ContinuityIndexResult


def sorted_index(index):
    return {key: sorted(set(value)) for key, value in sorted(index.items())}


class ContinuityIndexer:
    @staticmethod
    def build(verified_input):
        bundle, snapshot, annotations, sources, _ = decode(verified_input)
        groups = defaultdict(list)
        for aid, annotation in annotations.items():
            groups[
                relation_key(
                    annotation["subject_ref"],
                    annotation["related_ref"],
                    annotation["relation_type"],
                )
            ].append(aid)
        relations, annotation_relation, pairs, assignments = {}, {}, {}, {}
        refs, by_thread, by_ref, by_relation = (defaultdict(list) for _ in range(4))
        memberships, conflicts = {}, []
        known = {binding.ref for binding in snapshot.references}
        for key, aids in sorted(groups.items()):
            first = annotations[aids[0]]
            subject, related, kind = (
                first[x] for x in ("subject_ref", "related_ref", "relation_type")
            )
            states = {state: [] for state in ("UNREVIEWED", "CANDIDATE", "CONFIRMED", "REJECTED")}
            threads, support, unassigned = defaultdict(list), defaultdict(list), []
            for aid in aids:
                a = annotations[aid]
                states[a["review_status"]].append(aid)
                annotation_relation[aid] = key
                if a["thread_ref"] is None:
                    unassigned.append(aid)
                else:
                    threads[a["thread_ref"]].append(aid)
                    if a["review_status"] == "CONFIRMED":
                        support[a["thread_ref"]].append(aid)
            review_conflict = bool(states["CONFIRMED"] and states["REJECTED"])
            review_status = (
                "CONFLICTED"
                if review_conflict
                else "CONFIRMED"
                if states["CONFIRMED"]
                else "REJECTED"
                if states["REJECTED"]
                else "PENDING"
            )
            thread_status = (
                "CONFLICTED"
                if len(threads) > 1
                else "UNIQUE_ASSERTION"
                if threads
                else "NO_ASSERTION"
            )
            assignment = {
                "status": thread_status,
                "assertions_by_thread": sorted_index(threads),
                "unassigned_annotation_ids": unassigned,
                "review_status_by_annotation": {
                    aid: annotations[aid]["review_status"] for aid in aids
                },
                "confirmed_support_by_thread": sorted_index(support),
                "conflict": len(threads) > 1,
            }
            blockers = []
            if review_status != "CONFIRMED":
                blockers.append("REVIEW_" + review_status)
            if thread_status != "UNIQUE_ASSERTION":
                blockers.append("THREAD_" + thread_status)
            thread = next(iter(threads)) if len(threads) == 1 else None
            if thread is not None and not support[thread]:
                blockers.append("NO_CONFIRMED_EXPLICIT_THREAD_SUPPORT")
            if (
                subject not in known
                or related not in known
                or (thread is not None and thread not in known)
            ):
                blockers.append("UNRESOLVED_REFERENCES")
            relations[key] = {
                "continuity_relation_key": key,
                "subject_ref": subject,
                "related_ref": related,
                "relation_type": kind,
                "annotation_ids": aids,
                "review_summary": {
                    "status": review_status,
                    "annotation_ids_by_status": states,
                    "reviewers_by_annotation": {aid: annotations[aid]["reviewer"] for aid in aids},
                    "conflict": review_conflict,
                },
                "thread_assignment_summary": assignment,
                "resolution_summary": {
                    "context_hash": snapshot.semantic_hash,
                    "by_annotation": {aid: annotations[aid]["resolution_status"] for aid in aids},
                },
                "membership_blockers": blockers,
            }
            assignments[key] = assignment
            for ref in {subject, related}:
                refs[ref].append(key)
            pair = canonical_bytes([subject, related]).decode().rstrip("\n")
            pairs.setdefault(
                pair, {"subject_ref": subject, "related_ref": related, "relation_keys": []}
            )["relation_keys"].append(key)
            for conflict_type, active in (
                ("REVIEW_CONFLICT", review_conflict),
                ("THREAD_ASSIGNMENT_CONFLICT", len(threads) > 1),
            ):
                if active:
                    conflicts.append(
                        {"type": conflict_type, "relation_key": key, "annotation_ids": aids}
                    )
            if not blockers:
                for member, role in ((subject, "subject"), (related, "related")):
                    mid = membership_id(thread, member)
                    row = memberships.setdefault(
                        mid,
                        {
                            "membership_id": mid,
                            "thread_ref": thread,
                            "member_ref": member,
                            "resolution_context_hash": snapshot.semantic_hash,
                            "supporting_relations": {},
                        },
                    )
                    proof = row["supporting_relations"].setdefault(
                        key, {"annotation_ids": support[thread], "roles": []}
                    )
                    proof["roles"].append(role)
                    by_thread[thread].append(mid)
                    by_ref[member].append(mid)
                    by_relation[key].append(mid)
        for row in memberships.values():
            row["supporting_annotation_ids"] = sorted(
                {
                    aid
                    for proof in row["supporting_relations"].values()
                    for aid in proof["annotation_ids"]
                }
            )
        result = ContinuityIndexResult.model_validate(
            {
                "data_kind": bundle.data_kind,
                "annotations": annotations,
                "relation_index": {
                    "relations_by_key": relations,
                    "relation_by_annotation": annotation_relation,
                    "annotations_by_relation": dict(sorted(groups.items())),
                    "relations_by_ref": sorted_index(refs),
                    "relations_by_ref_pair": pairs,
                    "thread_assertions_by_relation": assignments,
                },
                "membership_index": {
                    "memberships_by_id": dict(sorted(memberships.items())),
                    "by_thread": sorted_index(by_thread),
                    "by_ref": sorted_index(by_ref),
                    "by_relation": sorted_index(by_relation),
                },
                "conflicts": conflicts,
                "counts": {
                    "annotations": len(annotations),
                    "relations": len(relations),
                    "review_conflicts": sum(c["type"] == "REVIEW_CONFLICT" for c in conflicts),
                    "thread_assignment_conflicts": sum(
                        c["type"] == "THREAD_ASSIGNMENT_CONFLICT" for c in conflicts
                    ),
                    "memberships": len(memberships),
                },
                "provenance": {
                    "bundle_byte_hash": digest_bytes(verified_input.bundle_bytes),
                    "input_manifest": [x.model_dump(mode="json") for x in bundle.input_manifest],
                    "source_artifact_hashes": bundle.source_artifact_hashes,
                    "snapshot_byte_hash": digest_bytes(
                        dict(verified_input.artifact_bytes)[bundle.resolution_snapshot]
                    ),
                    "annotation_sources": sources,
                },
                "resolution_context_hash": snapshot.semantic_hash,
                "deterministic_hash": "",
            }
        )
        return result.model_copy(
            update={"deterministic_hash": semantic_hash(result_semantics(result))}
        )
