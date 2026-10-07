"""Exact structural signatures: no message interpretation or fuzzy grouping."""

import math
import re

from ..models import AuditRecord, RecordType
from .models import Disposition, PatternSignature

DIMENSION_FIELDS = (
    "source_family",
    "source_object_type",
    "target_object_type",
    "object_type",
    "field",
    "field_name",
    "source_field",
    "target_field",
)
ELIGIBLE_TYPES = frozenset(
    {
        RecordType.VALIDATION_FINDING,
        RecordType.ADAPTATION_LOSS,
        RecordType.QUARANTINE,
        RecordType.SCHEMA_GAP,
        RecordType.REGISTRY_GAP,
    }
)
SUMMARY_TYPES = frozenset(
    {
        RecordType.TEST_RESULT,
        RecordType.GATE_RESULT,
        RecordType.IMMUTABILITY_EVENT,
        RecordType.DEBT_STATUS,
    }
)


class PatternInputError(ValueError):
    """Invalid input or nonconserving index; never silently drop occurrences."""


def disposition_for(record_type: RecordType) -> Disposition:
    if record_type in ELIGIBLE_TYPES:
        return Disposition.PATTERN_ELIGIBLE
    if record_type == RecordType.MAPPING_EVENT:
        return Disposition.TRACE_ONLY
    if record_type in SUMMARY_TYPES:
        return Disposition.SUMMARY_ONLY
    if record_type == RecordType.UNKNOWN_ENGINEERING_RECORD:
        return Disposition.OPAQUE_EXCLUDED
    raise PatternInputError(f"Unsupported record type: {record_type}")


def normalize_path_shape(path: str | None) -> str | None:
    if path is None or path == "":
        return path
    if not isinstance(path, str) or not path.startswith("/"):
        raise PatternInputError("Structural paths must be JSON Pointers or null")
    tokens = path[1:].split("/")
    if any(re.search(r"~(?![01])", token) for token in tokens):
        raise PatternInputError("Malformed JSON Pointer escape")
    # RFC 6901/6902 canonical array indexes only. No ID or business-token inference.
    return "/" + "/".join(
        "*" if re.fullmatch(r"0|[1-9][0-9]*", token) else token for token in tokens
    )


def build_signature(record: AuditRecord) -> PatternSignature:
    if disposition_for(record.record_type) != Disposition.PATTERN_ELIGIBLE:
        raise PatternInputError("Only eligible records have engineering signatures")
    source = record.metadata.get("source_record", {})
    if not isinstance(source, dict):
        # A valid AuditRecord may lack a structured source snapshot. Keep its
        # occurrence and top-level signature, with no invented dimensions.
        source = {}
    dimensions = {}
    for key in DIMENSION_FIELDS:
        # AuditRecord 0.1.0 has none of these top-level fields. Do not invent extras.
        if key in source:
            value = source[key]
            if type(value) not in {str, bool, int, float, type(None)}:
                raise PatternInputError(
                    f"Dimension {key} must be a JSON scalar, not an opaque payload"
                )
            if isinstance(value, float) and not math.isfinite(value):
                raise PatternInputError(f"Dimension {key} must be finite")
            dimensions[key] = value
    return PatternSignature(
        record_type=record.record_type,
        component=record.component,
        category=record.category,
        rule_id=record.rule_id,
        reason_code=record.reason_code,
        structured_dimensions=dict(sorted(dimensions.items())),
        source_path_shape=normalize_path_shape(record.source_path),
        target_path_shape=normalize_path_shape(record.target_path),
    )
