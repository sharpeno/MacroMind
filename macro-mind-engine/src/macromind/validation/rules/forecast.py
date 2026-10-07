from .common import compare_bounds, finding, resolution_reversals, time_bounds, unknown
from .temporal import forecast_relation


def admission(s):
    for obj in s.index.of_type("Forecast"):
        claim = s.index.get(obj.claim_ref)
        wrong_type = claim is not None and claim.object_type != "Claim"
        invalid = (
            wrong_type
            or forecast_relation(obj) == "after"
            or bool(resolution_reversals(obj.resolution_criteria))
        )
        for value in (obj.knowledge_cutoff, obj.prediction_window):
            bounds = time_bounds(value)
            invalid = invalid or bool(bounds and bounds[0] > bounds[1])
        missing = [
            field
            for field in ("claimant", "modal_strength", "resolution_criteria")
            if unknown(getattr(obj, field))
        ]
        if not time_bounds(obj.knowledge_cutoff):
            missing.append("knowledge_cutoff")
        if not time_bounds(obj.prediction_window):
            missing.append("prediction_window")
        if forecast_relation(obj) not in ("after", "not_after"):
            missing.append("cutoff_window_order")
        if not unknown(obj.resolution_criteria) and unknown(obj.resolution_criteria.description):
            missing.append("resolution_criteria.description")
        if claim is None:
            missing.append("claim_ref")
        if not unknown(obj.conditions):
            missing.append("structured_condition_endorsement")
        if obj.conditions is not None and unknown(obj.conditions):
            missing.append("conditions_unknown")
        outcome = "ERROR" if invalid else ("INDETERMINATE" if missing else "PASS")
        classification = {
            "ERROR": "ADMISSION_INVALID",
            "INDETERMINATE": "ADMISSION_INDETERMINATE",
            "PASS": "ADMISSION_STRUCTURALLY_SUPPORTED",
        }[outcome]
        yield finding(
            obj,
            outcome,
            message="Structural admission only; resolvability alone proves no classification.",
            admission=classification,
            unresolved=missing,
        )


def conditional(s):
    for obj in s.index.of_type("Forecast"):
        if obj.conditions is not None:
            yield finding(
                obj,
                "INDETERMINATE",
                "/conditions",
                "Canonical schema lacks structured condition endorsement; branch text is not proof.",
                branch_selection_recorded=not unknown(obj.branch_selection),
                schema_gap="conditional_endorsement",
            )


def resolution(s):
    for obj in s.index.of_type("Forecast"):
        criteria = obj.resolution_criteria
        reversals = resolution_reversals(criteria)
        outcome = "ERROR" if reversals else "INDETERMINATE"
        if (
            not reversals
            and not unknown(criteria)
            and all(
                time_bounds(getattr(criteria, f))
                for f in ("set_at", "approved_at", "evaluation_time")
            )
            and not unknown(criteria.scoring_permitted)
            and all(
                compare_bounds(
                    time_bounds(getattr(criteria, left)), time_bounds(getattr(criteria, right))
                )
                == "not_after"
                for left, right in (("set_at", "approved_at"), ("approved_at", "evaluation_time"))
            )
        ):
            outcome = "PASS"
        yield finding(
            obj,
            outcome,
            "/resolution_criteria",
            "Recorded resolution timing; no implicit scoring approval.",
            reversals=reversals,
        )
