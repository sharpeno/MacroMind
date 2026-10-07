import pytest
from macromind.audit import AuditInputBundle


@pytest.mark.parametrize(
    "severity", ["ERROR", "WARNING", "INDETERMINATE", "PASS", "INFO", "BLOCKING"]
)
def test_severity_exact(artifact, normalizer, severity):
    item = {
        "severity": severity,
        "outcome": "INDETERMINATE",
        "category": "recorded",
        "message": "This text says PASS ERROR but is not interpreted",
        "review_required": None,
    }
    record = normalizer.normalize_artifact(artifact({"issues": [item]})).records[0]
    assert record.severity == record.source_severity == record.normalized_severity_class == severity
    assert record.source_outcome == "INDETERMINATE"
    assert record.category == "recorded"
    assert record.review_required is None
    assert record.metadata["source_record"] == item


@pytest.mark.parametrize("outcome", ["PASS", "FAIL", "ERROR", "WARNING", "INDETERMINATE", None])
def test_gate_outcome_exact(artifact, normalizer, outcome):
    record = normalizer.normalize_artifact(
        artifact({"gates": [{"status": outcome}]}, "gate_result")
    ).records[0]
    assert record.record_type == "GATE_RESULT"
    assert record.source_outcome == outcome
    assert record.severity is None


@pytest.mark.parametrize(
    "kind,key,expected",
    [
        ("schema_gap_report", "gaps", "SCHEMA_GAP"),
        ("registry_gap_report", "gaps", "REGISTRY_GAP"),
        ("test_report", "cases", "TEST_RESULT"),
    ],
)
def test_distinct_types(artifact, normalizer, kind, key, expected):
    item = {"status": "unknown", "missing_structure": "recorded gap"}
    result = normalizer.normalize_artifact(artifact({key: [item]}, kind))
    assert result.records[0].record_type == expected
    assert result.records[0].metadata["source_record"] == item
    assert result.records[0].source_outcome == "unknown"


def test_adaptation_loss_quarantine_mapping_unknown(artifact, normalizer):
    content = {
        "losses": [{"severity": "BLOCKING", "description": "loss", "preserved_raw": True}],
        "quarantined_items": [{"reason_code": "missing", "raw_payload": {"x": None}}],
        "mapping_ledger": [
            {
                "operation": "DEFAULT_UNKNOWN",
                "semantic_change": False,
                "source_path": None,
                "target_path": "/x",
                "evidence": ["/old"],
            }
        ],
        "unknowns": [{"value": {"state": "unknown"}}],
        "warnings": ["No category inference"],
        "unsupported_fields": [{"value": None}],
    }
    result = normalizer.normalize_artifact(artifact(content, "adaptation_result"))
    assert [r.record_type for r in result.records[:3]] == [
        "ADAPTATION_LOSS",
        "QUARANTINE",
        "MAPPING_EVENT",
    ]
    assert result.records[0].severity == "BLOCKING"
    assert result.records[1].severity is None
    assert result.records[1].reason_code == "missing"
    assert result.records[2].evidence_refs == ["/old"]
    assert result.records[3].metadata["source_record"]["value"] == {"state": "unknown"}
    assert len(result.records) == 6


def test_debt_not_finding(artifact, normalizer):
    item = {"status": "partially_addressed_phase1_4", "remaining": "no resolution"}
    r = normalizer.normalize_artifact(artifact({"debts": {"D/02~": item}}, "debt_overlay")).records[
        0
    ]
    assert r.record_type == "DEBT_STATUS"
    assert r.source_outcome == item["status"]
    assert r.source_pointer == "/debts/D~102~0"


def test_immutability_empty_arrays_are_evidence(artifact, normalizer):
    r = normalizer.normalize_artifact(
        artifact({"checked_files": 4, "frozen_changed": []}, "immutability_report")
    )
    assert len(r.records) == 2
    assert all(x.record_type == "IMMUTABILITY_EVENT" and x.severity is None for x in r.records)
    assert r.records[1].metadata["source_record"] == []


@pytest.mark.parametrize(
    "content,kind",
    [
        ({"arbitrary": True}, "future_type"),
        ({"issues": "malformed"}, "validation_report"),
        ({"issues": [{"severity": 42}]}, "validation_report"),
        ({"severity": {"arbitrary": True}}, "future_type"),
        ([1, 2, 3], "validation_report"),
        ({"gate_status": "PASS"}, "manifest"),
    ],
)
def test_unsupported_never_lost(artifact, normalizer, content, kind):
    a = artifact(content, kind)
    r = normalizer.normalize_artifact(a)
    assert len(r.unsupported_inputs) == len(r.records) == 1
    assert r.unsupported_inputs[0]["sha256"] == a.sha256
    assert r.unsupported_inputs[0]["artifact_type"] == kind
    assert r.unsupported_inputs[0]["reason"]
    assert r.records[0].record_type == "UNKNOWN_ENGINEERING_RECORD"
    assert r.records[0].metadata["source_record"] == content


def test_no_deduplication_of_ten_thousand_losses(artifact, normalizer):
    a = artifact(
        {
            "losses": [{"severity": "WARNING", "description": "same"}] * 10000,
            "quarantined_items": [],
        },
        "adaptation_result",
    )
    r = normalizer.normalize_artifact(a)
    assert len(r.records) == len({x.record_id for x in r.records}) == 10000
    assert r.record_counts == {"ADAPTATION_LOSS": 10000}


def test_validator_views_not_duplicated(artifact, normalizer):
    issue = {"severity": "ERROR", "outcome": "ERROR"}
    a = artifact({"issues": [issue], "errors": [issue], "warnings": [], "indeterminate": []})
    assert len(normalizer.normalize_artifact(a).records) == 1


def test_empty_bundle(normalizer):
    result = normalizer.normalize_bundle(AuditInputBundle())
    assert result.records == result.unsupported_inputs == []


def test_no_auto_annotations_from_similar_text(artifact, normalizer):
    a = artifact(
        {
            "objects": [
                {"title": "Inflation outlook", "text": "rates rise"},
                {"title": "Inflation outlook", "text": "rates rise again"},
            ]
        },
        "analysis_objects",
    )
    result = normalizer.normalize_artifact(a)
    assert "annotations" not in result.model_dump()
    assert "thread_ref" not in result.model_dump()
    assert result.records[0].record_type == "UNKNOWN_ENGINEERING_RECORD"
