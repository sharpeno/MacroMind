from ..reference_contracts import references
from .common import finding


def duplicates(s):
    for identity, positions in s.index.groups.items():
        yield finding(
            identity,
            "ERROR" if len(positions) > 1 else "PASS",
            "/id",
            "Duplicate object id." if len(positions) > 1 else "Unique object id.",
            positions=positions,
        )


def types(s):
    for i, name in s.index.unknown_types.items():
        yield finding(
            s.index.raw_ref(i), "ERROR", "/object_type", "Unknown object type.", supplied_type=name
        )
    for obj in s.index.objects.values():
        yield finding(obj)


def resolution(s):
    for obj in s.index.objects.values():
        for contract, path, ref in references(obj):
            if contract.resolution in ("external", "local_step"):
                continue
            local = []
            if contract.resolution == "argument_node":
                local = [step.id for step in obj.steps]
            elif contract.resolution == "scenario_branch":
                local = [branch.id for branch in obj.branches]
            if ref in local:
                status = (
                    "ambiguous_local_and_global_id"
                    if contract.resolution == "argument_node" and ref in s.index.groups
                    else "resolved"
                )
                yield obj, contract, path, ref, status
                continue
            target = s.index.get(ref) if contract.resolution != "scenario_branch" else None
            if target is not None:
                status = (
                    "wrong_type"
                    if contract.target_types and target.object_type not in contract.target_types
                    else "resolved"
                )
            else:
                status = (
                    "absent_from_bundle"
                    if contract.resolution == "scenario_branch"
                    else s.index.unresolved_reason(ref)
                )
            yield obj, contract, path, ref, status


def wrong_types(s):
    for obj, contract, path, ref, status in resolution(s):
        if status in ("wrong_type", "resolved"):
            yield finding(
                obj,
                "ERROR" if status == "wrong_type" else "PASS",
                path,
                "Reference target type checked.",
                related=[ref],
                allowed_types=contract.target_types,
            )


def unresolved(s, mode):
    if s.context.validation_mode != mode:
        return
    for obj, _contract, path, ref, status in resolution(s):
        if status not in ("resolved", "wrong_type"):
            outcome = (
                "ERROR"
                if mode == "complete_bundle" and status == "absent_from_bundle"
                else "INDETERMINATE"
            )
            yield finding(obj, outcome, path, "Unresolved reference.", related=[ref], reason=status)


def complete(s):
    yield from unresolved(s, "complete_bundle")


def partial(s):
    yield from unresolved(s, "partial_bundle")


def self_refs(s):
    for obj in s.index.objects.values():
        for contract, path, ref in references(obj):
            if not contract.allow_self:
                yield finding(
                    obj,
                    "ERROR" if obj.id == ref else "PASS",
                    path,
                    "An active prior cannot refer to itself.",
                    related=[ref],
                )
