import copy
import json
from pathlib import Path

import pytest

from macromind.methods.timeline import evaluate, object_hash, render_timeline, save_new

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "phase1/method_timeline/run_001"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def packet(stage):
    return read(RUN / f"{stage}.input.json")


def previous():
    return read(RUN / "T0/snapshot.json")


def test_three_stages_preserve_update_hold_withdraw_and_unknown():
    prior = None
    results = []
    for stage in ["T0", "T1", "T2"]:
        prior = evaluate(packet(stage), ROOT, prior)
        results.append(prior)
    assert results[0]["judgments"][1]["state"] == "unknown"
    assert results[1]["judgments"][1]["state"] == "scheduled"
    assert results[2]["judgments"][1]["state"] == "observed"
    assert results[2]["changes"][2]["action"] == "WITHDRAW"
    assert all(r["judgments"][3]["state"] == "unknown" for r in results)
    assert all(not r["forecast_score_eligible"] for r in results)


def test_unused_future_source_still_rejected():
    data = packet("T0")
    data["sources"].append(packet("T2")["sources"][-1])
    with pytest.raises(ValueError, match="Future publication"):
        evaluate(data, ROOT)


def test_meeting_date_cannot_stand_in_for_publication_date():
    data = packet("T2")
    data["as_of"] = "2024-11-08"
    with pytest.raises(ValueError, match="Future publication"):
        evaluate(data, ROOT, read(RUN / "T1/snapshot.json"))


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda p: p.update(previous_sha256="0" * 64), "Predecessor"),
        (lambda p: p.update(as_of="2024-08-23"), "cutoffs"),
        (lambda p: p["sources"][0].update(sha256="0" * 64), "hash mismatch"),
        (lambda p: p["sources"][0].update(path="../核心主旨.md"), "path/hash"),
        (lambda p: p["judgments"][1].update(state="observed"), "cannot prove"),
        (lambda p: p["judgments"][2].update(state="observed"), "outcome evidence"),
        (lambda p: p["judgments"][3].update(state="observed"), "hidden plans"),
        (lambda p: p["judgments"][0].update(evidence_refs=["missing"]), "Unknown source"),
        (lambda p: p["judgments"].pop(), "Stable judgment"),
        (lambda p: p.update(forecast_score_eligible=True), "False"),
        (lambda p: p["sources"].append(copy.deepcopy(p["sources"][0])), "Duplicate"),
    ],
)
def test_invalid_transitions_and_provenance(mutation, match):
    data = packet("T1")
    mutation(data)
    with pytest.raises(ValueError, match=match):
        evaluate(data, ROOT, previous())


def test_relabeling_release_date_breaks_source_binding():
    data = packet("T2")
    data["sources"][-1]["published"] = "2024-11-07"
    with pytest.raises(ValueError, match="metadata mismatch"):
        evaluate(data, ROOT, read(RUN / "T1/snapshot.json"))


def test_saved_history_is_immutable(tmp_path):
    result = evaluate(packet("T0"), ROOT)
    target = tmp_path / "snapshot"
    save_new(result, target)
    before = (target / "snapshot.json").read_bytes()
    with pytest.raises(FileExistsError):
        save_new(result, target)
    assert (target / "snapshot.json").read_bytes() == before


def test_updating_does_not_mutate_predecessor():
    prior = previous()
    expected = object_hash(prior)
    evaluate(packet("T1"), ROOT, prior)
    assert object_hash(prior) == expected


def test_render_escapes_and_explains_hindsight():
    result = evaluate(packet("T0"), ROOT)
    result["changes"][0]["after"]["statement"] = "<script>alert(1)</script>"
    html = render_timeline([result])
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "不是盲测或真实预测成绩" in html
