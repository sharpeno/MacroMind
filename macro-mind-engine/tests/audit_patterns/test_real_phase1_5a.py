import json
from collections import Counter
from pathlib import Path

import pytest
from macromind.audit.ids import digest_bytes, semantic_hash
from macromind.audit.models import NormalizedAuditBundle
from macromind.audit.patterns import PatternAggregator, validate_conservation
from macromind.audit.patterns.signature import ELIGIBLE_TYPES

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "phase1/phase1_5a_normalization_report.json"


@pytest.fixture(scope="module")
def real():
    raw = SOURCE.read_bytes()
    b = NormalizedAuditBundle.model_validate(json.loads(raw))
    assert semantic_hash(b.semantic_payload()) == b.deterministic_hash
    return b, digest_bytes(raw), PatternAggregator().aggregate(b)


def test_real_counts_dynamic_and_complete(real):
    b, _, result = real
    expected = sum(count for kind, count in b.record_counts.items() if kind in ELIGIBLE_TYPES)
    assert result.eligible_occurrence_count == expected
    assert len(result.record_dispositions) == sum(b.record_counts.values()) == len(b.records)
    assert sum(result.disposition_counts.values()) == len(b.records)
    assert all(validate_conservation(result, b.records).values())


def test_real_full_drilldown_statistics(real):
    b, _, result = real
    records = {r.record_id: r for r in b.records}
    assert len({p.pattern_id for p in result.patterns}) == result.pattern_count
    for p in result.patterns:
        occurrences = [records[rid] for rid in p.occurrence_record_ids]
        assert len(occurrences) == p.occurrence_count
        assert p.artifact_count == len({r.source_artifact_id for r in occurrences})
        assert p.review_required_count == sum(r.review_required is True for r in occurrences)
        expected = Counter("null" if r.severity is None else r.severity for r in occurrences)
        assert p.severity_distribution == dict(expected)


def test_real_three_runs_immutable(real):
    b, byte_hash, first = real
    before = semantic_hash(b.semantic_payload())
    for _ in range(2):
        result = PatternAggregator().aggregate(b)
        assert result.semantic_bytes() == first.semantic_bytes()
        assert result.deterministic_hash == first.deterministic_hash
    assert semantic_hash(b.semantic_payload()) == before
    assert digest_bytes(SOURCE.read_bytes()) == byte_hash
