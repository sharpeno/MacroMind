from .common import finding, prior_status, unknown


def matches(s):
    for obj in s.index.of_type("AnalystMethodSignal"):
        outcome = "PASS"
        if obj.recurrence_match == "none" and obj.matched_prior_signal_refs:
            outcome = "ERROR"
        elif obj.recurrence_match in ("exact", "partial", "analogous") and (
            not obj.matched_prior_signal_refs
            or unknown(obj.matched_scope)
            or not obj.recurrence_evidence
        ):
            outcome = "INDETERMINATE"
        yield finding(
            obj,
            outcome,
            "/recurrence_match",
            "Match none has no active priors; uncertain plus first_observation is allowed. Match evidence is structural only.",
        )


def recurrence(s):
    for obj in s.index.of_type("AnalystMethodSignal"):
        if obj.recurrence_status not in ("repeated", "frequent", "candidate_pattern"):
            continue
        statuses = [prior_status(s, obj, ref) for ref in obj.matched_prior_signal_refs]
        outcome = (
            "PASS"
            if "eligible" in statuses
            else ("ERROR" if statuses and all(v == "future" for v in statuses) else "INDETERMINATE")
        )
        yield finding(
            obj,
            outcome,
            "/recurrence_status",
            "Pattern requires eligible historical support; no frequency is invented.",
            prior_statuses=statuses,
        )


def diagnostic(obj):
    return (
        getattr(obj, "expression_level", None) == "model_reconstruction"
        or getattr(obj, "analysis_context", None) == "model_diagnostic"
    )


def observer_attribution(s):
    for obj in s.index.of_type("AnalystMethodSignal"):
        observed = obj.observed_reasoner_id
        observer = obj.annotation_observer
        yield finding(
            obj,
            "INDETERMINATE" if unknown(observed) or unknown(observer) else "PASS",
            "/observed_reasoner_id",
            "Observed reasoner and annotation observer are independent roles; equal identities are allowed.",
            observed_reasoner=observed,
            annotation_observer=observer,
        )


def model_evidence(s):
    for obj in s.index.of_type("AnalystMethodSignal", "Heuristic"):
        refs = (
            obj.provenance
            if obj.object_type == "Heuristic"
            else obj.argument_refs
            + obj.claim_refs
            + obj.recurrence_evidence
            + obj.matched_prior_signal_refs
        )
        if diagnostic(obj):
            yield finding(
                obj,
                "WARNING",
                message="Diagnostic/model reconstruction signal is not creator-explicit evidence.",
            )
        for ref in sorted(set(refs)):
            target = s.index.get(ref)
            if target is None:
                continue
            outcome = "PASS"
            if diagnostic(target):
                outcome = "ERROR"
            elif target.object_type == "Argument" and any(
                diagnostic(step) for step in target.steps
            ):
                outcome = "WARNING"
            item = finding(
                obj,
                outcome,
                message="Analyst evidence must not promote model reconstruction; mixed arguments lack selected-edge evidence scope.",
                evidence=[ref],
                schema_gap="selected_edge_evidence_scope" if outcome == "WARNING" else None,
            )
            item["review_required"] = outcome != "PASS"
            yield item
