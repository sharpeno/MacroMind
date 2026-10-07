from copy import deepcopy

import pytest
from macromind.audit import AuditInputArtifact, AuditInputBundle, InputIntegrityError
from macromind.audit.ids import digest_bytes


def test_source_content_and_result_isolation(artifact, normalizer):
    source = {"issues": [{"object_ref": {"id": "a"}, "evidence_refs": [{"id": "b"}]}]}
    before = deepcopy(source)
    a = artifact(source)
    result = normalizer.normalize_artifact(a)
    result.records[0].metadata["source_record"]["object_ref"]["id"] = "changed"
    result.records[0].evidence_refs[0]["id"] = "changed"
    assert source == a.content == before


def test_expected_hash_mismatch_content(artifact):
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        artifact({"issues": []}, expected_sha256="0" * 64)


def test_expected_hash_file_and_unchanged(tmp_path, normalizer):
    p = tmp_path / "input.json"
    p.write_bytes(b'{"issues": []}')
    before = digest_bytes(p.read_bytes())
    with pytest.raises(InputIntegrityError):
        AuditInputArtifact.from_file(
            p,
            artifact_type="validation_report",
            phase="1.3",
            component="v",
            expected_sha256="0" * 64,
        )
    a = AuditInputArtifact.from_file(
        p, artifact_type="validation_report", phase="1.3", component="v", expected_sha256=before
    )
    normalizer.normalize_artifact(a)
    assert digest_bytes(p.read_bytes()) == before


def test_nested_mutation_detected(artifact, normalizer):
    a = artifact({"issues": []})
    a.content["issues"].append({"severity": "ERROR"})
    with pytest.raises(InputIntegrityError):
        normalizer.normalize_artifact(a)


def test_entire_bundle_preverified(artifact, normalizer, monkeypatch):
    from macromind.audit import normalize

    a = artifact({"issues": [{}]})
    b = artifact({"issues": []})
    bundle = AuditInputBundle(validation_reports=[a, b])
    b.content["issues"].append({"bad": True})

    def forbidden(*args):
        pytest.fail("Normalization began before all hashes verified")

    monkeypatch.setattr(normalize, "_source_items", forbidden)
    with pytest.raises(InputIntegrityError):
        normalizer.normalize_bundle(bundle)


def test_raw_content_tampering(tmp_path, normalizer):
    p = tmp_path / "input.json"
    p.write_bytes(b'{"issues": []}')
    a = AuditInputArtifact.from_file(
        p, artifact_type="validation_report", phase="1.3", component="v"
    )
    a.content["issues"].append({})
    with pytest.raises(InputIntegrityError, match="captured source bytes"):
        normalizer.normalize_artifact(a)


def test_duplicate_artifact_rejected(artifact, normalizer):
    a = artifact({"issues": []})
    with pytest.raises(InputIntegrityError, match="Duplicate artifact"):
        normalizer.normalize_bundle(AuditInputBundle(validation_reports=[a, a]))
