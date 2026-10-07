import copy
import json
from pathlib import Path

import pytest

from macromind.quality.semantic_review import validate_packet

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "phase1/extraction_quality/semantic_pilot_001"


def case(ep="EP003"):
    packet = json.loads((PILOT / (ep + ".packet.json")).read_bytes())
    root = ROOT / "phase1/batch_pilot/run_004" / ep
    return (
        packet,
        json.loads((root / "annotation.json").read_bytes()),
        json.loads((root / "segments.json").read_bytes()),
    )


@pytest.mark.parametrize("ep", ["EP002", "EP003", "EP005"])
def test_complete_packet_is_review_ready_never_approved(ep):
    result = validate_packet(*case(ep))
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert not result["semantic_acceptance"]
    assert not result["compile_authorization"]


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_axis",
        "invented_cue",
        "no_anchor",
        "false_approval",
        "stale_source",
        "stale_annotation",
        "duplicate_item",
        "retain_with_edit",
        "wrong_original",
        "outside_scope",
    ],
)
def test_invalid_dossier_is_rejected(mutation):
    p, a, s = case()
    item = p["items"][0]
    if mutation == "missing_axis":
        del item["dimensions"]["assumptions"]
    elif mutation == "invented_cue":
        item["evidence_cues"].append(99999)
    elif mutation == "no_anchor":
        item["dimensions"]["speaker_role"]["cue_ids"] = []
    elif mutation == "false_approval":
        item["human_status"] = "ACCEPTED"
    elif mutation == "stale_source":
        s[0]["quote"] += "changed"
    elif mutation == "stale_annotation":
        a["claims"][0][2] += "changed"
    elif mutation == "duplicate_item":
        p["items"].append(copy.deepcopy(item))
    elif mutation == "retain_with_edit":
        item["action"] = "retain"
    elif mutation == "wrong_original":
        item["original_statement"] += "changed"
    else:
        item["dimensions"]["speaker_role"]["cue_ids"] = [1]
    assert validate_packet(p, a, s)["status"] == "INVALID_PACKET"


def test_wrong_semantic_judgment_is_not_falsely_detected_by_structural_checks():
    p, a, s = case()
    p["items"][0]["dimensions"]["modality"]["assessment"] = "这是可能错误的自检解释。"
    result = validate_packet(p, a, s)
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["semantic_acceptance"] is False
