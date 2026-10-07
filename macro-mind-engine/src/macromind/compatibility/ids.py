from collections import Counter, defaultdict

from .detector import digest

ID_KEYS = {
    "Source": "source_id",
    "SourceVersion": "source_version_id",
    "SourceSegment": "source_segment_id",
    "SourceFamily": "family_id",
    "Claim": "claim_id",
    "ClaimOccurrence": "occurrence_id",
    "Actor": "actor_id",
    "Event": "event_id",
    "StructuralProcess": "process_id",
    "Indicator": "indicator_id",
    "IndicatorObservation": "observation_id",
    "Policy": "policy_id",
    "ExpectationSnapshot": "expectation_snapshot_id",
    "Assessment": "assessment_id",
    "Argument": "argument_id",
    "Mechanism": "mechanism_id",
    "MechanismUsage": "usage_id",
    "Scenario": "scenario_id",
    "Thesis": "thesis_id",
    "Forecast": "forecast_id",
    "Contradiction": "contradiction_id",
    "Heuristic": "heuristic_id",
    "AnalystMethodSignal": "signal_id",
    "ReviewQueueItem": "review_id",
}


def identity(raw, kind):
    key = "id" if "id" in raw else ID_KEYS.get(kind, "id")
    return key, raw.get(key)


def build_ids(records):
    counts = Counter()
    for _, kind, raw in records:
        if isinstance(raw, dict):
            _, value = identity(raw, kind)
            if isinstance(value, str) and value:
                counts[value] += 1
    assignments = {}
    refs = defaultdict(list)
    for path, kind, raw in records:
        if not isinstance(raw, dict):
            continue
        key, value = identity(raw, kind)
        old = value if isinstance(value, str) and value else None
        if old and counts[old] == 1:
            target = old
        else:
            # Content-derived namespace is independent of transport path and object order.
            target = "compat:" + str(kind) + ":" + digest({"kind": kind, "payload": raw})[:24]
        assignments[path] = (target, key, old)
        if old:
            refs[old].append((kind, target))
    duplicate_targets = {k for k, n in Counter(v[0] for v in assignments.values()).items() if n > 1}
    return assignments, refs, duplicate_targets
