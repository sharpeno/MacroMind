import hashlib
import json
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[1]
WORKSPACE = ENGINE.parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"


@pytest.fixture
def contract_root():
    return CONTRACT


@pytest.fixture
def contract_copy(tmp_path):
    import shutil

    target = tmp_path / "contract"
    shutil.copytree(CONTRACT, target)
    return target


def pytest_sessionstart(session):
    protected = WORKSPACE / "golden_sample_test"
    session.protected_hashes = {
        p.relative_to(WORKSPACE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in protected.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


@pytest.fixture(scope="session", autouse=True)
def original_artifacts_unchanged(request):
    yield
    current = {
        p.relative_to(WORKSPACE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (WORKSPACE / "golden_sample_test").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    assert current == request.session.protected_hashes
    baseline = ENGINE / "phase1/input_hashes.json"
    if baseline.exists():
        assert current == json.loads(baseline.read_text(encoding="utf-8"))
