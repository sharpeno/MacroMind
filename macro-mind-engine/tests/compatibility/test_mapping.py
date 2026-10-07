from macromind.compatibility.detector import digest
from macromind.compatibility.engine import leaves, pointer

from .helpers import canonical, legacy


def test_mapping_covers_all_canonical_leaves(compatibility):
    result = compatibility.adapt(legacy())
    targets = {m.target_path for m in result.mapping_ledger}
    expected = {
        "/canonical_bundle" + path
        for path, _ in leaves(result.canonical_bundle)
        if path.startswith("/objects/")
    }
    assert expected <= targets
    output = result.model_dump(mode="json")
    for mapping in result.mapping_ledger:
        assert not mapping.semantic_change
        assert digest(pointer(output, mapping.target_path)) == mapping.target_value_hash
        if mapping.source_path is not None:
            assert (
                digest(pointer(result.raw_document, mapping.source_path))
                == mapping.source_value_hash
            )


def test_cross_type_ids_and_refs(compatibility):
    value = legacy([{"claim_id": "shared", "statement": "claim", "source_refs": ["shared"]}])
    value["02_SOURCES"] = [{"source_id": "shared", "title": "source"}]
    result = compatibility.adapt(value)
    claim = canonical(result, "Claim")[0]
    source = canonical(result, "Source")[0]
    assert claim["id"] != source["id"] and claim["source_refs"] == [source["id"]]
    assert any(m.operation == "REF_MAP" for m in result.mapping_ledger)


def test_missing_ids_stable_and_order_permutation(compatibility):
    value = legacy([{"statement": "one"}, {"statement": "two"}])
    first = compatibility.adapt(value)
    value["08_CLAIMS"].reverse()
    second = compatibility.adapt(value)
    assert first.canonical_bundle == second.canonical_bundle
    assert (
        first.adaptation_manifest["canonical_bundle_hash"]
        == second.adaptation_manifest["canonical_bundle_hash"]
    )


def test_ambiguous_duplicate_identity_quarantined(compatibility):
    value = legacy(
        [{"claim_id": "same", "statement": "same"}, {"claim_id": "same", "statement": "same"}]
    )
    result = compatibility.adapt(value)
    assert result.status == "UNSUPPORTED" and result.quarantined_object_count == 2


def test_unresolved_ref_retained_not_invented(compatibility):
    result = compatibility.adapt(
        legacy([{"claim_id": "c", "statement": "C", "source_refs": ["outside"]}])
    )
    assert canonical(result, "Claim")[0]["source_refs"] == ["outside"]
    assert any(item.category == "REFERENCE_UNRESOLVED" for item in result.losses)


def test_real_mapping_hashes_and_coverage(real_results):
    for result in real_results.values():
        output = result.model_dump(mode="json")
        targets = {m.target_path for m in result.mapping_ledger}
        expected = {
            "/canonical_bundle" + path
            for path, _ in leaves(result.canonical_bundle)
            if path.startswith("/objects/")
        }
        assert expected <= targets
        for mapping in result.mapping_ledger:
            assert digest(pointer(output, mapping.target_path)) == mapping.target_value_hash
            if mapping.source_path is not None:
                assert (
                    digest(pointer(result.raw_document, mapping.source_path))
                    == mapping.source_value_hash
                )
        assert (
            result.source_object_count
            == result.canonical_object_count + result.quarantined_object_count
        )
