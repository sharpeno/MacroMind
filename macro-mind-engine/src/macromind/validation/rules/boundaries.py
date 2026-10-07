from .common import finding, time_bounds, unknown


def scenarios(s):
    forecasts = s.index.of_type("Forecast")
    for obj in s.index.of_type("Scenario"):
        shared = [f.id for f in forecasts if f.claim_ref in obj.claim_refs]
        yield finding(
            obj,
            "WARNING" if shared else "PASS",
            "/claim_refs",
            "Scenario branches do not constitute Forecast admission; type is preserved.",
            related=shared,
        )


def processes(s):
    for obj in s.index.of_type("StructuralProcess"):
        absent = not (
            obj.event_refs or obj.observation_refs or obj.policy_refs or obj.evidence_refs
        )
        period = time_bounds(obj.period)
        cross_period = bool(period and period[0] < period[1])
        single = len(obj.event_refs) == 1 and not obj.observation_refs and not cross_period
        yield finding(
            obj,
            "WARNING" if absent or single else "INDETERMINATE",
            message="Evidence must support a process; validator never promotes events.",
            evidence_absent=absent,
            single_event_without_cross_period_observation=single,
        )


def assessment(s):
    for obj in s.index.of_type("Assessment"):
        yield finding(
            obj,
            message="Assessment status belongs to the Assessment, never its target.",
            related=[obj.target_ref],
            observer=obj.observer,
            verification_status=obj.verification_status,
        )
    for i, obj in enumerate(s.index.raw):
        if obj.get("object_type") == "Claim" and "truth" in obj:
            yield finding(
                s.index.raw_ref(i),
                "ERROR",
                "/truth",
                "Claim has no truth field; assessment status cannot be propagated.",
            )


def usage(s):
    for obj in s.index.of_type("MechanismUsage"):
        target = s.index.get(obj.mechanism_ref)
        yield finding(
            obj,
            "PASS" if target and target.object_type == "Mechanism" else "INDETERMINATE",
            message="Usage analyst never becomes Mechanism author by propagation; equal ids are allowed.",
            usage_analyst=obj.analyst_id,
            mechanism_reasoner=getattr(target, "reasoner_id", None),
        )


def actors(s):
    for obj in s.index.of_type("Actor"):
        yield finding(obj, message="Location and roles are attributes, not identity merge keys.")


def comparison(s):
    for obj in s.index.of_type("IndicatorObservation"):
        basis = obj.comparison_basis
        if unknown(basis):
            yield finding(obj, "INDETERMINATE", "/comparison_basis", "Unknown comparison retained.")
            continue
        # Free text units are not a controlled unit vocabulary. Even a familiar
        # spelling cannot certify a conversion or dimensional equivalence.
        pp_unclear = basis.comparison_type == "percentage_point_change" and (
            unknown(basis.delta_unit)
            or basis.delta_unit not in ("pp", "percentage points", "percentage_point")
        )
        yield finding(
            obj,
            "WARNING" if pp_unclear else "INDETERMINATE",
            "/comparison_basis",
            "No baseline/delta calculation or percent-to-point conversion; typed unit semantics are absent.",
            schema_gap="comparison_unit_semantics",
            remaining_debt=["D16"],
            semantic_role=obj.semantic_role,
            recognition_stage=obj.recognition_stage,
        )
