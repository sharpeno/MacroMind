import pytest
from macromind.audit.ids import record_id
from macromind.audit.provenance import resolve_pointer


def test_every_record_resolves(artifact, normalizer):
    a = artifact({"issues": [{"rule_id": "R1", "severity": "ERROR"}, {"rule_id": "R2"}]})
    for r in normalizer.normalize_artifact(a).records:
        assert r.source_artifact_hash == a.sha256
        assert r.source_artifact_id == a.artifact_id
        assert resolve_pointer(a.content, r.source_pointer) == r.metadata["source_record"]
        assert r.record_id == record_id(a.sha256, r.source_pointer, r.record_type)


@pytest.mark.parametrize("pointer,expected", [("", {"a/b": {"~": [None]}}), ("/a~1b/~0/0", None)])
def test_pointer_escaping(pointer, expected):
    assert resolve_pointer({"a/b": {"~": [None]}}, pointer) == expected


@pytest.mark.parametrize("pointer", ["wrong", "/x/~2", "/x/01", "/x/-1", "/x/-", "/x/1", "/x/0/a"])
def test_invalid_pointer(pointer):
    with pytest.raises((ValueError, KeyError, IndexError)):
        resolve_pointer({"x": [None]}, pointer)
