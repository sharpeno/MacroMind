"""Enumerate explicit historical object sections without classifying statement text."""

from ..detector import key_name

SECTIONS = {
    "sources": "Source",
    "source_versions": "SourceVersion",
    "source_segments": "SourceSegment",
    "claims": "Claim",
    "claim_occurrences": "ClaimOccurrence",
    "actors": "Actor",
    "events": "Event",
    "structural_processes": "StructuralProcess",
    "indicators": "Indicator",
    "observations": "IndicatorObservation",
    "policies": "Policy",
    "expectation_snapshots": "ExpectationSnapshot",
    "veracity_assessments": "Assessment",
    "narrative_assessments": "Assessment",
    "arguments": "Argument",
    "mechanisms": "Mechanism",
    "mechanism_usage": "MechanismUsage",
    "scenarios": "Scenario",
    "theses": "Thesis",
    "forecasts": "Forecast",
    "contradictions": "Contradiction",
    "candidate_heuristics": "Heuristic",
    "review_queue": "ReviewQueueItem",
    "ma1_manual_review_queue": "ReviewQueueItem",
}


def escape(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def entries(document):
    if not isinstance(document, dict):
        return []
    result = []

    def section(value, kind, path):
        if isinstance(value, list):
            result.extend((path + "/" + str(i), kind, item) for i, item in enumerate(value))
        elif isinstance(value, dict) and kind == "ReviewQueueItem":
            for k, v in value.items():
                section(v, kind, path + "/" + escape(k))

    def scan(mapping, path=""):
        for k, value in mapping.items():
            name = key_name(k)
            pointer = path + "/" + escape(k)
            if name in SECTIONS:
                section(value, SECTIONS[name], pointer)
            elif name in (
                "actors_events_indicators_observations_policies",
                "indicators_observations",
                "auxiliary",
            ) and isinstance(value, dict):
                scan(value, pointer)
            elif name == "analyst_method_signals" and isinstance(value, dict):
                for group, items in value.items():
                    if isinstance(items, list):
                        for i, item in enumerate(items):
                            if isinstance(item, dict) and (
                                "signal_id" in item or "signal_type" in item
                            ):
                                result.append(
                                    (
                                        pointer + "/" + escape(group) + "/" + str(i),
                                        "AnalystMethodSignal",
                                        item,
                                    )
                                )
            elif name == "source_families_origin_families":
                if isinstance(value, list):
                    section(value, "SourceFamily", pointer)
                elif isinstance(value, dict) and isinstance(value.get("origin_families"), list):
                    section(value["origin_families"], "SourceFamily", pointer + "/origin_families")
            elif name == "objects" and isinstance(value, list):
                for i, item in enumerate(value):
                    result.append(
                        (
                            pointer + "/" + str(i),
                            item.get("object_type") if isinstance(item, dict) else None,
                            item,
                        )
                    )

    scan(document)
    return result
