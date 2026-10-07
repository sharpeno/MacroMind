"""Engineering Pattern Aggregation 0.1.0; independent of continuity annotations."""

from .aggregate import PatternAggregator, validate_conservation
from .models import (
    PATTERN_VERSION,
    AuditPattern,
    Disposition,
    PatternAggregationResult,
    PatternOccurrenceIndex,
    PatternSignature,
)
from .signature import PatternInputError, build_signature, disposition_for, normalize_path_shape

__all__ = [
    "PATTERN_VERSION",
    "AuditPattern",
    "Disposition",
    "PatternAggregationResult",
    "PatternAggregator",
    "PatternInputError",
    "PatternOccurrenceIndex",
    "PatternSignature",
    "build_signature",
    "disposition_for",
    "normalize_path_shape",
    "validate_conservation",
]
