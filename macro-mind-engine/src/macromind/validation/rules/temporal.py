from pydantic import BaseModel

from macromind.schema.common import TimeReference

from .common import compare_bounds, finding, prior_status, time_bounds, utc


def temporal_values(value, path=""):
    if isinstance(value, TimeReference):
        yield path, value
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            yield from temporal_values(getattr(value, name), f"{path}/{name}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from temporal_values(item, f"{path}/{i}")


def intervals(s):
    for obj in s.index.objects.values():
        for path, value in temporal_values(obj):
            bounds = time_bounds(value)
            outcome = (
                "INDETERMINATE"
                if bounds is None
                else ("ERROR" if bounds[0] > bounds[1] else "PASS")
            )
            yield finding(
                obj,
                outcome,
                path,
                "Only explicitly recorded timezone-aware bounds can be compared.",
            )


def forecast_relation(obj):
    cutoff, window = time_bounds(obj.knowledge_cutoff), time_bounds(obj.prediction_window)
    start = utc(getattr(obj.prediction_window, "start", None))
    if not cutoff or not window or start is None or window[0] > window[1]:
        return "unknown"
    return compare_bounds(cutoff, (start, start))


def forecasts(s):
    for obj in s.index.of_type("Forecast"):
        relation = forecast_relation(obj)
        yield finding(
            obj,
            "ERROR"
            if relation == "after"
            else ("PASS" if relation == "not_after" else "INDETERMINATE"),
            "/prediction_window",
            "Forecast cutoff must not follow prediction window start.",
            comparison=relation,
        )


def priors(s):
    for obj in s.index.of_type("AnalystMethodSignal"):
        for ref in obj.matched_prior_signal_refs:
            status = prior_status(s, obj, ref)
            yield finding(
                obj,
                {"future": "ERROR", "eligible": "PASS", "unknown": "INDETERMINATE"}[status],
                "/matched_prior_signal_refs",
                "Prior chronology uses content time, never names.",
                related=[ref],
                chronology=status,
            )


def source_axes(s):
    for obj in s.index.of_type("SourceVersion"):
        bounds = [
            time_bounds(getattr(obj, field))
            for field in ("content_time", "published_at", "captured_at")
        ]
        yield finding(
            obj,
            "PASS" if all(bounds) else "INDETERMINATE",
            message="Content, publication and capture are independent axes; none substitutes for another.",
        )
