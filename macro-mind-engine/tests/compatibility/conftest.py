from pathlib import Path

import pytest
from macromind.compatibility import CompatibilityEngine

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"


@pytest.fixture(scope="session")
def compatibility():
    return CompatibilityEngine(CONTRACT, REGISTRY)


@pytest.fixture(scope="session")
def real_results(compatibility):
    # File paths select fixtures through recorded lineage, never adapter behavior.
    paths = {
        "summary": WORKSPACE / "golden_sample_test/golden_report.md",
        "pre": WORKSPACE / "golden_sample_test/golden_sample_002/golden_sample_002.json",
        "v03": WORKSPACE / "golden_sample_test/golden_sample_003/golden_sample_003.json",
        "accepted4": WORKSPACE
        / "golden_sample_test/golden_sample_004/golden_sample_004.ma1_accepted.json",
        "accepted5": WORKSPACE
        / "golden_sample_test/golden_sample_005/golden_sample_005.ma1_accepted.json",
    }
    return {name: compatibility.adapt_file(path) for name, path in paths.items()}
