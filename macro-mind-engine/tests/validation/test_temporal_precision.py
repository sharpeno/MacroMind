import pytest

from .helpers import has, obj


@pytest.mark.parametrize("endpoint", ["start", "end"])
def test_single_endpoint_does_not_invent_an_instant(engine, endpoint):
    value = obj(
        "Source", published_at={"text": "incomplete interval", endpoint: "2026-09-01T00:00:00Z"}
    )
    report = engine.validate([value])
    assert has(report, "V-TEMP001", "INDETERMINATE") and not report.errors
