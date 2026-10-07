import json

from .conftest import ROOT, WORKSPACE
from .helpers import canonical


def test_summary_only_no_reconstruction(real_results):
    result = real_results["summary"]
    assert result.source_family == "SUMMARY_ONLY_LEGACY" and result.status == "PARTIAL"
    assert not result.canonical_bundle["objects"] and result.canonical_reconstruction_forbidden
    assert result.raw_document == (WORKSPACE / "golden_sample_test/golden_report.md").read_text(
        encoding="utf8"
    )


def test_actual_pre_ma_v03_families(real_results):
    assert real_results["pre"].source_family == "LEGACY_PRE_MA"
    assert real_results["v03"].source_family == "V0_3_LEGACY"
    for name in ("pre", "v03"):
        result = real_results[name]
        assert result.canonical_object_count > 0 and result.unknowns
        assert result.status in ("PARTIAL", "LOSSY_BUT_SAFE")


def test_actual_accepted_ma1(real_results):
    for name in ("accepted4", "accepted5"):
        result = real_results[name]
        assert result.source_family == "MA1_COMPAT" and result.detection_status == "EXACT"
        assert result.canonical_object_count > 0
        assert result.raw_document["ma1_migration"]["human_acceptance"] is True
        assert any(u["source_path"] == "/finalization" for u in result.unsupported_fields)


def test_gs005_accepted_scenario_decision(real_results):
    result = real_results["accepted5"]
    original = result.raw_document
    assert original["finalization"]["human_decisions"]["MA1-C005"] == "keep_scenario_only"
    accepted = [s for s in original["21_SCENARIOS"] if "C005" in s["claim_refs"]]
    assert accepted and accepted[0]["forecast_admitted"] is False
    assert any("C005" in s["claim_refs"] for s in canonical(result, "Scenario"))
    assert not any(f["claim_ref"] == "C005" for f in canonical(result, "Forecast"))
    claim = next(c for c in original["08_CLAIMS"] if c["claim_id"] == "C005")
    assert claim["semantic_role"] == "unknown" and claim["recognition_stage"] == "unknown"
    assert claim["comparison_basis"]["comparison_type"] == "unknown"
    excluded = original["ma1_migration"]["machine_use_policy"]["excluded_occurrence_evidence"]
    for identity in excluded:
        assert not any(o["id"] == identity for o in canonical(result, "ClaimOccurrence"))
        assert any(
            q.raw_payload.get("occurrence_id") == identity
            and q.reason_code == "explicit_historical_exclusion"
            for q in result.quarantined_items
        )


def test_gs004_decisions_not_reinterpreted(real_results):
    result = real_results["accepted4"]
    original = result.raw_document
    decisions = original["finalization"]["human_decisions"]
    assert decisions["MA1-FUTURE-LEAK-MS02"] == "accept_quarantined_future_prior"
    assert decisions["MA1-COMPARISON-OB20"] == "accept_raw_value_comparison_unknown"
    signals = canonical(result, "AnalystMethodSignal")
    original_signals = [
        s
        for group in original["26_ANALYST_METHOD_SIGNALS"].values()
        if isinstance(group, list)
        for s in group
        if isinstance(s, dict) and "signal_id" in s
    ]
    for signal in signals:
        source = next(s for s in original_signals if s["signal_id"] == signal["id"])
        for field in (
            "matched_prior_signal_refs",
            "recurrence_match",
            "reasoner_id",
            "observed_reasoner_id",
            "annotation_observer",
        ):
            if field in source:
                assert signal[field] == source[field]
    observation = next(o for o in canonical(result, "IndicatorObservation") if o["id"] == "OB20")
    assert observation["comparison_basis"]["comparison_type"] == "unknown"


def test_lineage_uses_completion_hashes():
    value = json.loads((ROOT / "phase1/phase1_4_artifact_lineage.json").read_text(encoding="utf8"))
    accepted = [i for i in value["artifacts"] if i["status"] == "accepted"]
    assert len(accepted) == 2
    assert all(i["authority_level"] == "accepted_with_completion_evidence" for i in accepted)
    assert any(i["transition_type"] == "accepted_hotfix" for i in accepted)
