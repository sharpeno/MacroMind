from pathlib import Path

import pytest
from macromind.validation import ValidatorEngine

ENGINE = Path(__file__).resolve().parents[2]
CONTRACT = ENGINE.parent / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ENGINE / "registries/v0_3"


@pytest.fixture(scope="session")
def engine():
    return ValidatorEngine(CONTRACT, REGISTRY)
