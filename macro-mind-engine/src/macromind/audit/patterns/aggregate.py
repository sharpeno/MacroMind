"""Read-only aggregation by exact signature; complete reversible occurrence indexes."""

import re
from collections import Counter, defaultdict

from ..ids import canonical_bytes, semantic_hash
from ..models import AuditRecord, NormalizedAuditBundle, RecordType
from .models import AuditPattern, Disposition, PatternAggregationResult, PatternOccurrenceIndex
from .signature import PatternInputError, build_signature, disposition_for


def distribution_key(value: object) -> str:
    """Preserve null/string/typed JSON distinctions without assigning severity."""
    if value is None:
        return "null"
    if isinstance(value, str):
        if value != "null" and not value.startswith(("str:", "json:")):
            return value
        return "str:" + canonical_bytes(value).decode("utf-8").rstrip("\n")
    return "json:" + canonical_bytes(value).decode("utf-8").rstrip("\n")


def distribution(values) -> dict[str, int]:
    return dict(sorted(Counter(distribution_key(value) for value in values).items()))


def _validate_record(record: AuditRecord) -> None:
    if not isinstance(record, AuditRecord) or not isinstance(record.record_type, RecordType):
        raise PatternInputError("Expected a valid Phase 1.5A AuditRecord")
    for key in ("record_id", "source_artifact_id", "source_artifact_hash"):
        if not isinstance(getattr(record, key), str) or not getattr(record, key):
            raise PatternInputError(f"Missing or damaged {key}")
    for key in ("phase", "component", "source_pointer"):
        if not isinstance(getattr(record, key), str):
            raise PatternInputError(f"Damaged {key}")
    for key in (
        "category",
        "rule_id",
        "reason_code",
        "severity",
        "source_severity",
        "normalized_severity_class",
        "message",
        "source_path",
        "target_path",
    ):
        value = getattr(record, key)
        if value is not None and not isinstance(value, str):
            raise PatternInputError(f"Damaged {key}")
    if re.fullmatch(r"[0-9a-f]{64}", record.source_artifact_hash) is None:
        raise PatternInputError("Damaged source_artifact_hash")
    if record.review_required is not None and type(record.review_required) is not bool:
        raise PatternInputError("Damaged review_required")
    if not isinstance(record.metadata, dict):
        raise PatternInputError("Damaged metadata")
    if not isinstance(record.evidence_refs, list):
        raise PatternInputError("Damaged evidence_refs")
    if record.source_pointer and (
        not record.source_pointer.startswith("/") or re.search(r"~(?![01])", record.source_pointer)
    ):
        raise PatternInputError("Damaged source_pointer")


def validate_conservation(
    result: PatternAggregationResult, records: list[AuditRecord]
) -> dict[str, bool]:
    """Check completeness, uniqueness, exact disposition and both index directions."""
    ids = [r.record_id for r in records]
    if len(set(ids)) != len(ids):
        raise PatternInputError("Duplicate input record_id")
    expected = {r.record_id: disposition_for(r.record_type) for r in records}
    eligible = {
        rid for rid, disposition in expected.items() if disposition == Disposition.PATTERN_ELIGIBLE
    }
    if result.record_dispositions != expected:
        raise PatternInputError("Missing, extra or incorrect record disposition")
    expected_counts = {d.value: sum(value == d for value in expected.values()) for d in Disposition}
    if result.disposition_counts != expected_counts:
        raise PatternInputError("Disposition count mismatch")
    by_pattern = result.pattern_occurrence_index.by_pattern
    by_record = result.pattern_occurrence_index.by_record
    patterns = {p.pattern_id: p for p in result.patterns}
    if len(patterns) != len(result.patterns) or set(patterns) != set(by_pattern):
        raise PatternInputError("Duplicate or missing pattern identity")
    occurrences = [rid for p in result.patterns for rid in p.occurrence_record_ids]
    if len(occurrences) != len(set(occurrences)):
        raise PatternInputError("Duplicate occurrence assignment")
    if set(occurrences) != eligible or set(by_record) != eligible:
        raise PatternInputError("Eligible occurrence missing or ineligible occurrence assigned")
    for pid, pattern in patterns.items():
        if pattern.occurrence_record_ids != by_pattern[pid] or any(
            by_record[rid] != pid for rid in by_pattern[pid]
        ):
            raise PatternInputError("Bidirectional index mismatch")
        if pattern.occurrence_count != len(by_pattern[pid]):
            raise PatternInputError("Pattern occurrence count mismatch")
    if result.eligible_occurrence_count != len(eligible) or sum(
        p.occurrence_count for p in result.patterns
    ) != len(eligible):
        raise PatternInputError("Eligible count is not conserved")
    if result.pattern_count != len(patterns):
        raise PatternInputError("Pattern count mismatch")
    return {
        "dispositions_complete": True,
        "eligible_conserved": True,
        "exactly_once": True,
        "bidirectional_index": True,
    }


class PatternAggregator:
    def aggregate(
        self, bundle: NormalizedAuditBundle | list[AuditRecord]
    ) -> PatternAggregationResult:
        input_hash = None
        if isinstance(bundle, NormalizedAuditBundle):
            records = bundle.records
        elif isinstance(bundle, list):
            records = bundle
        else:
            raise PatternInputError("Expected NormalizedAuditBundle or AuditRecord list")
        if not isinstance(records, list):
            raise PatternInputError("Damaged record collection")
        for record in records:
            _validate_record(record)
        if isinstance(bundle, NormalizedAuditBundle):
            if dict(Counter(r.record_type.value for r in records)) != bundle.record_counts:
                raise PatternInputError("Normalized bundle record_counts mismatch")
            if semantic_hash(bundle.semantic_payload()) != bundle.deterministic_hash:
                raise PatternInputError("Normalized bundle semantic hash mismatch")
            input_hash = bundle.deterministic_hash
        if len({r.record_id for r in records}) != len(records):
            raise PatternInputError("Duplicate input record_id")
        groups = defaultdict(list)
        signatures = {}
        dispositions = {}
        artifacts = {d.value: set() for d in Disposition}
        types = {d.value: Counter() for d in Disposition}
        for record in sorted(records, key=lambda r: r.record_id):
            disposition = disposition_for(record.record_type)
            dispositions[record.record_id] = disposition
            artifacts[disposition.value].add(record.source_artifact_id)
            types[disposition.value][record.record_type.value] += 1
            if disposition != Disposition.PATTERN_ELIGIBLE:
                continue
            signature = build_signature(record)
            pid = signature.pattern_id()
            if pid in signatures and signatures[pid] != signature:
                raise PatternInputError("Pattern signature hash collision")
            signatures[pid] = signature
            groups[pid].append(record)
        patterns = []
        by_pattern, by_record = {}, {}
        for pid in sorted(groups):
            occurrences = groups[pid]
            ids = [r.record_id for r in occurrences]
            source_ids = sorted({r.source_artifact_id for r in occurrences})
            signature = signatures[pid]
            patterns.append(
                AuditPattern(
                    pattern_id=pid,
                    signature=signature,
                    **signature.model_dump(),
                    occurrence_count=len(ids),
                    artifact_count=len(source_ids),
                    occurrence_record_ids=ids,
                    source_artifact_ids=source_ids,
                    severity_distribution=distribution(r.severity for r in occurrences),
                    outcome_distribution=distribution(r.source_outcome for r in occurrences),
                    review_required_count=sum(r.review_required is True for r in occurrences),
                    example_record_ids=ids[:5],
                )
            )
            by_pattern[pid] = ids.copy()
            by_record.update({rid: pid for rid in ids})
        result = PatternAggregationResult(
            input_normalization_hash=input_hash,
            patterns=patterns,
            pattern_occurrence_index=PatternOccurrenceIndex(
                by_pattern=by_pattern, by_record=dict(sorted(by_record.items()))
            ),
            record_dispositions=dispositions,
            disposition_counts={
                d.value: sum(v == d for v in dispositions.values()) for d in Disposition
            },
            disposition_artifact_counts={d: len(ids) for d, ids in sorted(artifacts.items())},
            record_types_by_disposition={
                d: dict(sorted(c.items())) for d, c in sorted(types.items())
            },
            eligible_occurrence_count=len(by_record),
            pattern_count=len(patterns),
            deterministic_hash="",
        )
        validate_conservation(result, records)
        return result.model_copy(
            update={"deterministic_hash": semantic_hash(result.semantic_payload())}
        )
