import json
from pathlib import Path

import pytest
from macromind.audit import AuditInputArtifact, AuditInputBundle, AuditNormalizer
from macromind.audit.ids import digest_bytes
from macromind.audit.provenance import resolve_pointer

ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    ("validation_reports", "validation_report", "phase1_3_evidence/run_002/cli_partial.stdout.txt"),
    ("adaptation_results", "adaptation_result", "phase1_4_evidence/run_002/pre.adaptation.json"),
    ("schema_gap_reports", "schema_gap_report", "phase1_4_schema_gap.json"),
    ("registry_gap_reports", "registry_gap_report", "phase1_4_registry_gap.json"),
    ("immutability_reports", "immutability_report", "phase1_4_immutability_report.json"),
    ("gate_results", "gate_result", "phase1_4_gate_result.json"),
    ("test_reports", "test_report", "phase1_4_test_report.json"),
    ("debt_overlays", "debt_overlay", "phase1_4_debt_overlay.json"),
    ("manifests", "manifest", "phase1_4_manifest.json"),
]


@pytest.fixture(scope="module")
def real_bundle():
    baseline = json.loads(
        (ROOT / "phase1/phase1_5a_input_hashes.json").read_text(encoding="utf-8")
    )["protected"]
    groups = {}
    for group, kind, rel in INPUTS:
        path = ROOT / "phase1" / rel
        expected = baseline[path.relative_to(ROOT.parent).as_posix()]
        groups[group] = [
            AuditInputArtifact.from_file(
                path,
                artifact_type=kind,
                phase="1.3" if group == "validation_reports" else "1.4",
                component=kind,
                expected_sha256=expected,
            )
        ]
    return AuditInputBundle(**groups)


@pytest.fixture(scope="module")
def real_normalized(real_bundle):
    return AuditNormalizer().normalize_bundle(real_bundle)


def test_real_supported_smoke(real_normalized):
    assert len(real_normalized.input_manifest) == 9
    assert len(real_normalized.unsupported_inputs) == 1
    assert real_normalized.unsupported_inputs[0]["artifact_type"] == "manifest"
    assert set(real_normalized.record_counts) == {
        "VALIDATION_FINDING",
        "ADAPTATION_LOSS",
        "QUARANTINE",
        "MAPPING_EVENT",
        "SCHEMA_GAP",
        "REGISTRY_GAP",
        "IMMUTABILITY_EVENT",
        "GATE_RESULT",
        "TEST_RESULT",
        "DEBT_STATUS",
        "UNKNOWN_ENGINEERING_RECORD",
    }


def test_real_all_provenance_and_fidelity(real_bundle, real_normalized):
    sources = {a.artifact_id: a for a in real_bundle.artifacts()}
    for record in real_normalized.records:
        a = sources[record.source_artifact_id]
        source = resolve_pointer(a.content, record.source_pointer)
        assert source == record.metadata["source_record"]
        assert record.source_artifact_hash == a.sha256
        if isinstance(source, dict) and record.record_type != "UNKNOWN_ENGINEERING_RECORD":
            assert record.severity == source.get("severity")
            assert record.source_outcome == source.get(
                "outcome", source.get("status", source.get("current_outcome"))
            )


def test_real_three_runs_and_source_bytes(real_bundle, real_normalized):
    for _ in range(2):
        result = AuditNormalizer().normalize_bundle(real_bundle)
        assert result.deterministic_hash == real_normalized.deterministic_hash
        assert result.semantic_payload() == real_normalized.semantic_payload()
    for a in real_bundle.artifacts():
        assert digest_bytes(Path(a.path_or_label).read_bytes()) == a.sha256
