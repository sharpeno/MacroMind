import hashlib
import json

import pytest
from macromind.compatibility.detector import serialized

from .helpers import legacy


def test_three_runs_identical(compatibility):
    outputs = [compatibility.adapt(legacy(ma1=True)) for _ in range(3)]
    assert outputs[0] == outputs[1] == outputs[2]
    assert serialized(outputs[0].canonical_bundle) == serialized(outputs[2].canonical_bundle)


def test_filename_directory_metamorphism(compatibility, tmp_path):
    data = json.dumps(legacy(ma1=True), ensure_ascii=False).encode("utf8")
    paths = [
        tmp_path / "GS004" / "sample_002.json",
        tmp_path / "random" / "banana.json",
        tmp_path / "arbitrary" / "whatever.anyname",
    ]
    results = []
    for path in paths:
        path.parent.mkdir()
        path.write_bytes(data)
        results.append(compatibility.adapt_file(path))
        assert hashlib.sha256(path.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()
    assert results[0] == results[1] == results[2]


def test_in_place_and_overwrite_forbidden(compatibility, tmp_path):
    path = tmp_path / "input.json"
    data = json.dumps(legacy()).encode()
    path.write_bytes(data)
    with pytest.raises(ValueError, match="same file"):
        compatibility.adapt_file(path, path)
    output = tmp_path / "output.json"
    output.write_text("historical", encoding="utf8")
    with pytest.raises(ValueError, match="overwrite"):
        compatibility.adapt_file(path, output)
    assert path.read_bytes() == data and output.read_text(encoding="utf8") == "historical"


def test_adaptation_manifest(compatibility, tmp_path):
    source = tmp_path / "input.json"
    output = tmp_path / "view.json"
    source.write_text(json.dumps(legacy()), encoding="utf8")
    result = compatibility.adapt_file(source, output)
    assert json.loads(output.read_text(encoding="utf8")) == result.model_dump(mode="json")
    assert (
        json.loads((tmp_path / "view.adaptation_manifest.json").read_text(encoding="utf8"))
        == result.adaptation_manifest
    )
