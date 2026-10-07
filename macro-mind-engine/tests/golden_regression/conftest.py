"""Real immutable Golden fixtures, never copied into invented canonical records."""

from pathlib import Path

import pytest
from macromind.compatibility import CompatibilityEngine

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"
PATHS = {
    "GS001": WORKSPACE / "golden_sample_test/golden_report.md",
    **{
        f"GS{n:03}": WORKSPACE
        / f"golden_sample_test/golden_sample_{n:03}/golden_sample_{n:03}{'.ma1_accepted' if n >= 4 else ''}.json"
        for n in range(2, 6)
    },
}


@pytest.fixture(scope="session")
def golden_engine():
    return CompatibilityEngine(CONTRACT, REGISTRY)


@pytest.fixture(scope="session")
def goldens(golden_engine):
    return {name: golden_engine.adapt_file(path) for name, path in PATHS.items()}


def objects(result, kind):
    return [x for x in result.canonical_bundle["objects"] if x["object_type"] == kind]
