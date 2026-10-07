from datetime import datetime, timezone

from macromind.schema.common import TimeReference, UnknownValue

from ..models import RuleOutcome


def finding(
    obj,
    outcome=RuleOutcome.PASS,
    field="",
    message="Check passed.",
    related=(),
    evidence=(),
    **details,
):
    return dict(
        object_ref=obj.id if hasattr(obj, "id") else obj,
        outcome=RuleOutcome(outcome),
        field_path=field,
        message=message,
        related_refs=sorted(set(related)),
        evidence_refs=sorted(set(evidence)),
        review_required=outcome in ("WARNING", "INDETERMINATE"),
        details=details,
    )


def unknown(value):
    return value is None or isinstance(value, UnknownValue) or value == "unknown"


def utc(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        return None
    return value.astimezone(timezone.utc)


def time_bounds(value):
    if not isinstance(value, TimeReference):
        return None
    start, end = utc(value.start), utc(value.end)
    # Missing endpoints are never inferred. A known instant is start == end.
    if start is None or end is None:
        return None
    if (value.start is not None and start is None) or (value.end is not None and end is None):
        return None
    return start, end


def compare_bounds(left, right):
    if not left or not right or left[0] > left[1] or right[0] > right[1]:
        return "unknown"
    if left[0] > right[1]:
        return "after"
    if left[1] <= right[0]:
        return "not_after"
    return "overlap"


def content_time(state, ref, visited=None):
    obj = state.index.get(ref)
    if obj is None:
        return None
    override = state.context.time_overrides.get(ref)
    if override is not None:
        point = utc(override)
        return (point, point) if point else None
    visited = set(visited or ())
    if ref in visited:
        return None
    visited.add(ref)
    if obj.object_type in ("SourceVersion", "SourceSegment"):
        own = time_bounds(obj.content_time)
        if own:
            return own
        if obj.object_type == "SourceSegment" and obj.source_version_ref:
            return content_time(state, obj.source_version_ref, visited)
    if obj.object_type == "AnalystMethodSignal" and obj.source_segment_refs:
        times = [content_time(state, r, visited) for r in obj.source_segment_refs]
        if all(times):
            return min(t[0] for t in times), max(t[1] for t in times)
    return None


def prior_status(state, signal, ref):
    prior = content_time(state, ref)
    limits = []
    for value in (state.context.knowledge_cutoff, state.context.current_content_time):
        point = utc(value)
        if point:
            limits.append((point, point))
    current = content_time(state, signal.id)
    if current:
        limits.append(current)
    if not prior or not limits:
        return "unknown"
    comparisons = [compare_bounds(prior, limit) for limit in limits]
    if "after" in comparisons:
        return "future"
    return "eligible" if all(c == "not_after" for c in comparisons) else "unknown"


def resolution_reversals(criteria):
    if unknown(criteria):
        return []
    wrong = []
    for field in ("set_at", "approved_at", "evaluation_time"):
        bounds = time_bounds(getattr(criteria, field))
        if bounds and bounds[0] > bounds[1]:
            wrong.append(f"{field}:start>end")
    for left, right in (
        ("set_at", "approved_at"),
        ("set_at", "evaluation_time"),
        ("approved_at", "evaluation_time"),
    ):
        if (
            compare_bounds(
                time_bounds(getattr(criteria, left)), time_bounds(getattr(criteria, right))
            )
            == "after"
        ):
            wrong.append(f"{left}>{right}")
    return wrong
