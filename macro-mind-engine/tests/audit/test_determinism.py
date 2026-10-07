from macromind.audit import AuditInputArtifact, AuditInputBundle
from macromind.audit.ids import canonical_bytes, semantic_hash


def test_three_runs_same_ids_order_hash(artifact, normalizer):
    a = artifact({"issues": [{"severity": "WARNING"}, {"outcome": "INDETERMINATE"}]})
    runs = [normalizer.normalize_artifact(a) for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    assert runs[0].deterministic_hash == semantic_hash(runs[0].semantic_payload())


def test_filename_directory_metamorphism(tmp_path, normalizer):
    raw = b'{"issues": [{"severity": "ERROR"}]}\r\n'
    paths = [tmp_path / "a.json", tmp_path / "different" / "banana.json"]
    results = []
    for p in paths:
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(raw)
        a = AuditInputArtifact.from_file(
            p, artifact_type="validation_report", phase="1.3", component="validator"
        )
        results.append(normalizer.normalize_artifact(a))
        assert p.read_bytes() == raw
    assert results[0].semantic_payload() == results[1].semantic_payload()
    assert results[0].deterministic_hash == results[1].deterministic_hash
    assert results[0].records == results[1].records


def test_caller_operational_metadata_excluded(artifact, normalizer):
    a = artifact({"issues": [{}]}, source_metadata={"created_at": "today", "machine": "one"})
    b = artifact({"issues": [{}]}, source_metadata={"created_at": "tomorrow", "machine": "two"})
    assert (
        normalizer.normalize_artifact(a).deterministic_hash
        == normalizer.normalize_artifact(b).deterministic_hash
    )


def test_input_order_invariance(artifact, normalizer):
    a, b = artifact({"issues": [{"rule_id": "a"}]}), artifact({"issues": [{"rule_id": "b"}]})
    assert normalizer.normalize_bundle(
        AuditInputBundle(validation_reports=[a, b])
    ) == normalizer.normalize_bundle(AuditInputBundle(validation_reports=[b, a]))


def test_canonical_utf8_keys_newline():
    assert canonical_bytes({"z": "汉", "a": None}) == '{"a":null,"z":"汉"}\n'.encode()
