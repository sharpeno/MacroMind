"""Synthetic evidence only: explicit contexts, adversarial inputs and indexes."""

from copy import deepcopy
from itertools import product

import pytest
from macromind.audit.continuity_index import (
    ContinuityIndexer,
    ContinuityIndexError,
    load_input_bundle,
    load_result_bytes,
    serialize_input_bundle,
    verify_result,
)
from macromind.audit.continuity_index.identity import membership_id, relation_key, result_semantics
from macromind.audit.continuity_index.resolution import strict_json
from macromind.audit.ids import canonical_bytes, digest_bytes, semantic_hash


def annotation(
    reviewer="alice",
    status="CONFIRMED",
    thread="T",
    subject="A",
    related="B",
    kind="NEW_EVIDENCE",
    **extra,
):
    return dict(
        subject_ref=subject,
        related_ref=related,
        relation_type=kind,
        reviewer=reviewer,
        review_status=status,
        thread_ref=thread,
        **extra,
    )


def fixture(payloads, refs=("A", "B", "C", "T", "U"), data_kind="SYNTHETIC", label="fixture"):
    objects = canonical_bytes({ref: {"id": ref} for ref in refs})
    source = canonical_bytes(payloads)
    bindings = [
        dict(
            ref=ref,
            declared_object_type=None,
            source_artifact_id="objects",
            source_artifact_sha256=digest_bytes(objects),
            source_pointer="/" + ref.replace("~", "~0").replace("/", "~1"),
        )
        for ref in refs
    ]
    snapshot = dict(
        snapshot_version="1.0",
        authority_id="explicit-test-authority",
        source_version="fixture-1",
        references=sorted(bindings, key=lambda x: x["ref"]),
        source_artifact_hashes={"objects": digest_bytes(objects)},
    )
    snapshot["semantic_hash"] = semantic_hash(snapshot)
    artifacts = {"objects": objects, "annotations": source, "snapshot": canonical_bytes(snapshot)}
    trusted = dict(
        authority_id=snapshot["authority_id"],
        source_version=snapshot["source_version"],
        snapshot_sha256=digest_bytes(artifacts["snapshot"]),
        data_kind=data_kind,
    )
    bundle = dict(
        contract_version="1.0",
        data_kind=data_kind,
        annotation_payloads=payloads,
        annotation_sources=[
            dict(
                annotation_index=i,
                source_artifact_id="annotations",
                source_artifact_hash=digest_bytes(source),
                source_pointer=f"/{i}",
                payload_hash=semantic_hash(p),
                raw_payload=p,
            )
            for i, p in enumerate(payloads)
        ],
        resolution_snapshot="snapshot",
        input_manifest=[
            dict(artifact_id=k, sha256=digest_bytes(v), data_kind=data_kind, path_or_label=label)
            for k, v in artifacts.items()
        ],
        source_artifact_hashes={k: digest_bytes(v) for k, v in artifacts.items()},
        deterministic_hash="",
    )
    return bundle, artifacts, trusted


def verified(payloads, **kwargs):
    bundle, artifacts, trusted = fixture(payloads, **kwargs)
    raw = serialize_input_bundle(bundle, artifacts, trusted)
    return load_input_bundle(raw, artifacts, trusted)


def build(payloads, **kwargs):
    return ContinuityIndexer.build(verified(payloads, **kwargs))


def only_relation(result):
    return next(iter(result.relation_index.relations_by_key.values()))


@pytest.mark.parametrize(
    "left,right", list(product(["UNREVIEWED", "CANDIDATE", "CONFIRMED", "REJECTED"], repeat=2))
)
def test_review_matrix(left, right):
    result = build([annotation(status=left), annotation(reviewer="bob", status=right)])
    states = {left, right}
    expected = (
        "CONFLICTED"
        if {"CONFIRMED", "REJECTED"} <= states
        else "CONFIRMED"
        if "CONFIRMED" in states
        else "REJECTED"
        if "REJECTED" in states
        else "PENDING"
    )
    assert only_relation(result).review_summary.status == expected
    assert result.counts["memberships"] == (2 if expected == "CONFIRMED" else 0)
    assert result.counts["relations"] == 1


@pytest.mark.parametrize("thread1,thread2", list(product([None, "T", "U"], repeat=2)))
def test_thread_matrix(thread1, thread2):
    result = build([annotation(thread=thread1), annotation(reviewer="bob", thread=thread2)])
    asserted = {x for x in [thread1, thread2] if x is not None}
    expected = (
        "CONFLICTED" if len(asserted) > 1 else "UNIQUE_ASSERTION" if asserted else "NO_ASSERTION"
    )
    assert only_relation(result).thread_assignment_summary.status == expected
    assert result.counts["memberships"] == (2 if len(asserted) == 1 else 0)


def test_candidate_cannot_borrow_confirmation():
    result = build([annotation(thread=None), annotation(reviewer="bob", status="CANDIDATE")])
    assert result.counts["memberships"] == 0
    assert "NO_CONFIRMED_EXPLICIT_THREAD_SUPPORT" in only_relation(result).membership_blockers


def test_unresolved_candidate_conflicts_with_confirmed_thread():
    result = build([annotation(), annotation(reviewer="bob", status="CANDIDATE", thread="unknown")])
    assert result.counts["thread_assignment_conflicts"] == 1
    assert result.counts["memberships"] == 0


def test_relation_identity_direction_kind_and_exclusions():
    r = build(
        [
            annotation(),
            annotation(reviewer="bob", thread="U"),
            annotation(reviewer="carol", subject="B", related="A"),
            annotation(reviewer="dave", kind="COUNTER_EVIDENCE"),
        ]
    )
    assert r.counts["relations"] == 3
    assert relation_key("A", "B", "NEW_EVIDENCE") != relation_key("B", "A", "NEW_EVIDENCE")
    pair = r.relation_index.relations_by_ref_pair['["A","B"]']
    assert len(pair["relation_keys"]) == 2
    assert r.counts["review_conflicts"] == 0


def test_no_transitive_or_cross_relation_conflict():
    r = build(
        [
            annotation(),
            annotation(reviewer="bob", subject="B", related="C"),
            annotation(reviewer="carol", thread="U"),
        ]
    )
    assert relation_key("A", "C", "NEW_EVIDENCE") not in r.relation_index.relations_by_key
    assert r.counts["relations"] == 2
    assert set(r.membership_index.by_ref) == {"B", "C"}
    assert r.counts["memberships"] == 2


def test_membership_dedup_complete_proof_and_reverse_indexes():
    v = verified([annotation(), annotation(reviewer="bob"), annotation(subject="B", related="C")])
    r = ContinuityIndexer.build(v)
    assert r.counts["memberships"] == 3
    row = r.membership_index.memberships_by_id[membership_id("T", "B")]
    assert len(row["supporting_relations"]) == 2
    assert {role for p in row["supporting_relations"].values() for role in p["roles"]} == {
        "subject",
        "related",
    }
    assert sum(len(p["annotation_ids"]) for p in row["supporting_relations"].values()) == 3
    assert verify_result(r, v)["status"] == "PASS"
    for aid, key in r.relation_index.relation_by_annotation.items():
        assert aid in r.relation_index.annotations_by_relation[key]


def test_self_relation_retains_both_roles():
    r = build([annotation(related="A")])
    assert r.counts["memberships"] == 1
    proof = next(
        iter(
            next(iter(r.membership_index.memberships_by_id.values()))[
                "supporting_relations"
            ].values()
        )
    )
    assert proof["roles"] == ["subject", "related"]


@pytest.mark.parametrize(
    "change",
    [
        {},
        {"created_at": "2026-01-01T00:00:00Z"},
        {"review_notes": "different"},
        {"review_status": "REJECTED"},
    ],
)
def test_duplicate_ids_are_hard_errors(change):
    a = annotation()
    with pytest.raises(ContinuityIndexError) as error:
        verified([a, {**a, **change}])
    assert error.value.code == (
        "DUPLICATE_ANNOTATION_ID" if not change else "ANNOTATION_ID_CONTENT_CONFLICT"
    )


@pytest.mark.parametrize(
    "change",
    [
        {"reviewer": None},
        {"reviewer": "  "},
        {"subject_ref": "missing"},
        {"related_ref": "missing"},
        {"thread_ref": "missing"},
    ],
)
def test_invalid_confirmed_never_downgraded(change):
    with pytest.raises(ContinuityIndexError, match="CONTRACT_VALIDATION_ERROR"):
        verified([{**annotation(), **change}])


def test_resolution_claim_is_recomputed_preserved():
    r = build([annotation(status="CANDIDATE", subject="missing", resolution_status="RESOLVED")])
    aid = next(iter(r.annotations))
    assert r.annotations[aid]["resolution_status"] == "UNRESOLVED"
    assert r.provenance["annotation_sources"][aid]["claimed_resolution_status"] == "RESOLVED"
    assert r.counts["memberships"] == 0
    r2 = build([annotation(resolution_status="UNRESOLVED")])
    assert next(iter(r2.annotations.values()))["resolution_status"] == "RESOLVED"


def test_payload_cannot_supply_known_refs():
    with pytest.raises(ContinuityIndexError, match="PAYLOAD_KNOWN_REFS_FORBIDDEN"):
        verified([annotation(known_refs=["A", "B", "T"])])


def test_exact_refs_without_type_prefix_inference():
    r = build([annotation(subject=" A", status="CANDIDATE")])
    assert next(iter(r.annotations.values()))["resolution_status"] == "UNRESOLVED"
    r = build(
        [annotation(subject="Thread:not-a-thread", thread="plain")],
        refs=("Thread:not-a-thread", "B", "plain"),
    )
    assert r.counts["memberships"] == 2


def test_empty_real_and_three_identical_runs():
    v = verified([], refs=(), data_kind="REAL")
    outputs = [
        canonical_bytes(ContinuityIndexer.build(v).model_dump(mode="json")) for _ in range(3)
    ]
    assert outputs[0] == outputs[1] == outputs[2]
    assert set(ContinuityIndexer.build(v).counts.values()) == {0}


def test_order_filename_and_prose_invariant():
    payloads = [annotation(), annotation(reviewer="bob", subject="B", related="C")]
    original = build(payloads)
    reordered = build(list(reversed(payloads)), label="renamed")
    assert original.deterministic_hash == reordered.deterministic_hash
    assert original.provenance != reordered.provenance
    changed = build(
        [
            {
                **a,
                "review_notes": "note",
                "metadata": {"x": 1},
                "created_at": "2026-01-01T00:00:00Z",
            }
            for a in payloads
        ]
    )
    assert original.deterministic_hash == changed.deterministic_hash
    assert original.annotations != changed.annotations


def test_raw_bytes_unchanged_and_confirmed_reload():
    b, a, t = fixture([annotation()])
    before = deepcopy(a)
    raw = serialize_input_bundle(b, a, t)
    v = load_input_bundle(raw, a, t)
    r = ContinuityIndexer.build(v)
    output = canonical_bytes(r.model_dump(mode="json"))
    assert load_result_bytes(output, digest_bytes(output), v) == r
    assert a == before
    assert strict_json(raw)["annotation_payloads"] == b["annotation_payloads"]


@pytest.mark.parametrize(
    "raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e999}', b"\xff", b"{"]
)
def test_strict_json(raw):
    with pytest.raises(ContinuityIndexError):
        strict_json(raw)


@pytest.mark.parametrize(
    "mutation",
    [
        "artifact",
        "authority",
        "version",
        "trust_hash",
        "mixed",
        "manifest",
        "payload",
        "bundle_hash",
        "missing_source",
        "missing_snapshot",
    ],
)
def test_untrusted_input_hard_errors(mutation):
    b, a, t = fixture([annotation()])
    raw = serialize_input_bundle(b, a, t)
    b = strict_json(raw)
    if mutation == "artifact":
        a["objects"] += b" "
    elif mutation == "authority":
        t["authority_id"] = "other"
    elif mutation == "version":
        t["source_version"] = "other"
    elif mutation == "trust_hash":
        t["snapshot_sha256"] = "0" * 64
    elif mutation == "mixed":
        b["input_manifest"][0]["data_kind"] = "REAL"
    elif mutation == "manifest":
        b["input_manifest"].append(b["input_manifest"][0])
    elif mutation == "payload":
        b["annotation_payloads"][0]["review_notes"] = "altered"
    elif mutation == "bundle_hash":
        b["deterministic_hash"] = "0" * 64
    elif mutation == "missing_source":
        b["annotation_sources"] = []
    elif mutation == "missing_snapshot":
        b["resolution_snapshot"] = "missing"
    with pytest.raises(ContinuityIndexError):
        load_input_bundle(canonical_bytes(b), a, t)


@pytest.mark.parametrize("mutation", ["duplicate", "pointer", "hash", "semantic", "undeclared"])
def test_invalid_snapshot_even_when_re_pinned(mutation):
    b, a, t = fixture([annotation()])
    s = strict_json(a["snapshot"])
    if mutation == "duplicate":
        s["references"].append(s["references"][0])
    elif mutation == "pointer":
        s["references"][0]["source_pointer"] = "/absent"
    elif mutation == "hash":
        s["references"][0]["source_artifact_sha256"] = "0" * 64
    elif mutation == "undeclared":
        s["source_artifact_hashes"] = {}
    semantic = {k: v for k, v in s.items() if k != "semantic_hash"}
    semantic["references"] = sorted(semantic["references"], key=lambda x: x["ref"])
    s["semantic_hash"] = "0" * 64 if mutation == "semantic" else semantic_hash(semantic)
    a["snapshot"] = canonical_bytes(s)
    h = digest_bytes(a["snapshot"])
    t["snapshot_sha256"] = h
    b["source_artifact_hashes"]["snapshot"] = h
    next(x for x in b["input_manifest"] if x["artifact_id"] == "snapshot")["sha256"] = h
    with pytest.raises(ContinuityIndexError):
        serialize_input_bundle(b, a, t)


@pytest.mark.parametrize("mutation", ["bytes", "semantic", "reverse", "membership", "provenance"])
def test_output_tampering(mutation):
    v = verified([annotation()])
    r = ContinuityIndexer.build(v)
    raw = canonical_bytes(r.model_dump(mode="json"))
    expected = digest_bytes(raw)
    if mutation == "bytes":
        with pytest.raises(ContinuityIndexError):
            load_result_bytes(raw + b" ", expected, v)
        return
    if mutation == "semantic":
        r.annotations[next(iter(r.annotations))]["review_status"] = "REJECTED"
    elif mutation == "reverse":
        r.relation_index.relation_by_annotation.clear()
    elif mutation == "membership":
        next(iter(r.membership_index.memberships_by_id.values()))["supporting_relations"].clear()
    elif mutation == "provenance":
        r.provenance["bundle_byte_hash"] = "0" * 64
    # Even an attacker recomputing both hashes must not bypass source verification.
    r = r.model_copy(update={"deterministic_hash": semantic_hash(result_semantics(r))})
    raw = canonical_bytes(r.model_dump(mode="json"))
    with pytest.raises(ContinuityIndexError):
        load_result_bytes(raw, digest_bytes(raw), v)


def test_real_synthetic_separation():
    real = build([], refs=(), data_kind="REAL")
    synthetic = build([], refs=(), data_kind="SYNTHETIC")
    assert real.deterministic_hash != synthetic.deterministic_hash
    b, a, t = fixture([])
    raw = serialize_input_bundle(b, a, t)
    t["data_kind"] = "REAL"
    with pytest.raises(ContinuityIndexError, match="DATA_KIND_MISMATCH"):
        load_input_bundle(raw, a, t)


def test_verified_handle_does_not_bypass_revalidation():
    from dataclasses import replace

    v = verified([annotation()])
    artifacts = dict(v.artifact_bytes)
    artifacts["objects"] += b" "
    forged = replace(v, artifact_bytes=tuple(artifacts.items()))
    with pytest.raises(ContinuityIndexError, match="ARTIFACT_HASH_MISMATCH"):
        ContinuityIndexer.build(forged)


@pytest.mark.parametrize("pointer", ["/01", "/missing", "no-leading-slash", "/~2"])
def test_annotation_pointer_errors(pointer):
    b, a, t = fixture([annotation()])
    b["annotation_sources"][0]["source_pointer"] = pointer
    with pytest.raises(ContinuityIndexError, match="INVALID_SOURCE_POINTER"):
        serialize_input_bundle(b, a, t)


def test_all_explicit_support_retained_after_duplicate_membership():
    r = build([annotation(), annotation(reviewer="bob"), annotation(kind="COUNTER_EVIDENCE")])
    assert r.counts["relations"] == 2
    assert r.counts["memberships"] == 2
    assert r.counts["review_conflicts"] == 0
    for row in r.membership_index.memberships_by_id.values():
        assert len(row["supporting_relations"]) == 2
        assert sum(len(p["annotation_ids"]) for p in row["supporting_relations"].values()) == 3


def test_bad_external_descriptor_has_machine_error():
    b, a, t = fixture([annotation()])
    raw = serialize_input_bundle(b, a, t)
    with pytest.raises(ContinuityIndexError, match="TRUST_DESCRIPTOR_ERROR") as error:
        load_input_bundle(raw, a, {})
    assert error.value.as_dict()["code"] == "TRUST_DESCRIPTOR_ERROR"


def test_nonempty_three_runs_and_snapshot_permutation():
    b, a, t = fixture([annotation(), annotation(reviewer="bob", subject="B", related="C")])
    raw = serialize_input_bundle(b, a, t)
    v = load_input_bundle(raw, a, t)
    outputs = [
        canonical_bytes(ContinuityIndexer.build(v).model_dump(mode="json")) for _ in range(3)
    ]
    assert outputs[0] == outputs[1] == outputs[2]
    snapshot = strict_json(a["snapshot"])
    snapshot["references"].reverse()
    a["snapshot"] = canonical_bytes(snapshot)
    sha = digest_bytes(a["snapshot"])
    t["snapshot_sha256"] = sha
    b["source_artifact_hashes"]["snapshot"] = sha
    next(x for x in b["input_manifest"] if x["artifact_id"] == "snapshot")["sha256"] = sha
    second = ContinuityIndexer.build(load_input_bundle(serialize_input_bundle(b, a, t), a, t))
    assert second.deterministic_hash == strict_json(outputs[0])["deterministic_hash"]


def test_malformed_output_has_machine_error():
    v = verified([annotation()])
    r = ContinuityIndexer.build(v).model_dump(mode="json")
    del r["annotations"][next(iter(r["annotations"]))]["subject_ref"]
    raw = canonical_bytes(r)
    with pytest.raises(ContinuityIndexError, match="RESULT_INTEGRITY_ERROR"):
        load_result_bytes(raw, digest_bytes(raw), v)


def test_required_contract_fields_and_complete_source_payload():
    b, a, t = fixture([annotation(), annotation(reviewer="bob")])
    raw = serialize_input_bundle(b, a, t)
    assert strict_json(raw)["annotation_sources"][0]["raw_payload"] == b["annotation_payloads"][0]
    result = ContinuityIndexer.build(load_input_bundle(raw, a, t))
    relation = only_relation(result)
    assert relation.continuity_relation_key in result.relation_index.relations_by_key
    assert set(relation.thread_assignment_summary.review_status_by_annotation.values()) == {
        "CONFIRMED"
    }
    for row in result.membership_index.memberships_by_id.values():
        assert set(row["supporting_annotation_ids"]) == set(result.annotations)
    b["annotation_sources"][0]["raw_payload"] = {}
    with pytest.raises(ContinuityIndexError, match="PAYLOAD_MISMATCH"):
        serialize_input_bundle(b, a, t)
