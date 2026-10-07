import json
from pathlib import Path

import pytest

from macromind.methods.baseline import WorkingBaseline, render_baselines

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "phase1/method_prototype/run_003"


def items():
    return json.loads((RUN / "baselines.json").read_text(encoding="utf-8"))


def test_working_judgment_can_exist_with_unknown_evidence():
    for item in items():
        b = WorkingBaseline.model_validate(item)
        assert b.working_judgment and b.consequences
        assert b.evidence_state == "unknown"
        assert not b.absence_implies_nonexistence
        assert not b.monitoring_active


@pytest.mark.parametrize(
    "change",
    [
        {"absence_used_as_counterevidence": True},
        {"absence_implies_nonexistence": True},
        {"monitoring_active": True},
        {"upgrade_triggers": []},
        {"working_judgment": " "},
    ],
)
def test_missing_evidence_does_not_silently_prove_absence(change):
    data = items()[0]
    data.update(change)
    with pytest.raises(ValueError):
        WorkingBaseline.model_validate(data)


def test_approved_content_preserved():
    previous = ROOT / "phase1/method_prototype/run_002"
    assert (RUN / "inference.json").read_bytes() == (previous / "inference.json").read_bytes()
    html = (RUN / "TRACE.html").read_text(encoding="utf-8")
    assert html.replace(render_baselines(items()), "", 1) == (previous / "TRACE.html").read_text(
        encoding="utf-8"
    )


def test_html_escapes_and_duplicate_ids_fail():
    data = items()
    data[0]["working_judgment"] = "<script>bad</script>"
    assert "<script>" not in render_baselines(data)
    with pytest.raises(ValueError):
        render_baselines([data[0], data[0]])
