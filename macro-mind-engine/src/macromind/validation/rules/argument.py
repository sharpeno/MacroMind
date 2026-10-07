from collections import Counter, defaultdict, deque

from .common import finding, unknown


def step_ids(s):
    for obj in s.index.of_type("Argument"):
        duplicates = sorted(k for k, v in Counter(step.id for step in obj.steps).items() if v > 1)
        yield finding(
            obj,
            "ERROR" if duplicates else "PASS",
            "/steps",
            "Step ids must be unique.",
            duplicates=duplicates,
        )


def fragile(s):
    for obj in s.index.of_type("Argument"):
        refs = obj.most_fragile_step
        if unknown(refs) or not refs:
            yield finding(
                obj, "INDETERMINATE", "/most_fragile_step", "Fragility is explicitly unassessed."
            )
            continue
        valid = {step.id for step in obj.steps}
        for i in range(len(obj.steps)):
            valid.update((f"steps/{i}", f"/steps/{i}", f"#/steps/{i}", f"{obj.id}/steps/{i}"))
        for ref in refs:
            yield finding(
                obj,
                "PASS" if ref in valid else "ERROR",
                "/most_fragile_step",
                "Fragile reference must designate a local step.",
                related=[ref],
            )


def graph(obj):
    # Step ids denote inference nodes. Explicit edges retain step attribution and
    # resolve aliases without substituting an overall reasoner or rewriting nodes.
    edges = defaultdict(set)
    for step in obj.steps:
        node = ("step", step.id)
        edges[node]
        for premise in step.premises:
            src = (
                ("step", premise)
                if any(premise == st.id for st in obj.steps)
                else ("object", premise)
            )
            edges[src].add(node)
        if step.conclusion_ref:
            dst = (
                ("step", step.conclusion_ref)
                if any(step.conclusion_ref == st.id for st in obj.steps)
                else ("object", step.conclusion_ref)
            )
            # A step naming itself as its result is an alias, not a causal edge.
            if dst != node:
                edges[node].add(dst)
                edges[dst]
    return edges


def cycles(s):
    for obj in s.index.of_type("Argument"):
        if any(step.id in s.index.groups for step in obj.steps):
            yield finding(
                obj,
                "INDETERMINATE",
                "/steps",
                "Local step and global object ids collide; graph interpretation is ambiguous.",
            )
            continue
        edges = graph(obj)
        degree = {node: 0 for node in edges}
        for targets in edges.values():
            for target in targets:
                degree[target] = degree.get(target, 0) + 1
        queue = deque(node for node in degree if degree[node] == 0)
        count = 0
        while queue:
            node = queue.popleft()
            count += 1
            for target in edges[node]:
                degree[target] -= 1
                if degree[target] == 0:
                    queue.append(target)
        yield finding(
            obj,
            "ERROR" if count != len(degree) else "PASS",
            "/steps",
            "Argument directed graph must be acyclic.",
            cyclic_or_dependent_nodes=sorted(":".join(n) for n, d in degree.items() if d),
        )


def orphans(s):
    for obj in s.index.of_type("Argument"):
        if any(step.id in s.index.groups for step in obj.steps):
            yield finding(
                obj,
                "INDETERMINATE",
                "/steps",
                "Ambiguous local/global ids prevent orphan classification.",
            )
            continue
        if not obj.final_conclusion:
            yield finding(obj, "INDETERMINATE", "/final_conclusion", "Final conclusion is unknown.")
        edges = graph(obj)
        reverse = defaultdict(set)
        for node, targets in edges.items():
            for target in targets:
                reverse[target].add(node)
        final = (
            ("step", obj.final_conclusion)
            if any(obj.final_conclusion == st.id for st in obj.steps)
            else ("object", obj.final_conclusion)
        )
        ancestors, todo = set(), [final]
        while todo:
            node = todo.pop()
            if node not in ancestors:
                ancestors.add(node)
                todo.extend(reverse[node])
        for i, step in enumerate(obj.steps):
            incomplete = not step.premises or not step.conclusion_ref
            disconnected = obj.final_conclusion is not None and ("step", step.id) not in ancestors
            yield finding(
                obj,
                "WARNING" if incomplete or disconnected else "PASS",
                f"/steps/{i}",
                "Check step connection to the recorded final conclusion.",
                incomplete=incomplete,
                disconnected=disconnected,
            )


def attribution(s):
    for obj in s.index.of_type("Argument"):
        for i, step in enumerate(obj.steps):
            missing = (
                unknown(step.reasoner_id)
                or unknown(step.expression_level)
                or unknown(step.analysis_context)
            )
            yield finding(
                obj,
                "INDETERMINATE" if missing else "PASS",
                f"/steps/{i}/reasoner_id",
                "Per-edge attribution is preserved independently of overall reasoner.",
                overall_reasoner=obj.reasoner_id,
                edge_reasoner=step.reasoner_id,
                expression_level=step.expression_level,
                analysis_context=step.analysis_context,
            )


def semantic_gap(s):
    for obj in s.index.of_type("Argument"):
        yield finding(
            obj,
            "INDETERMINATE",
            "/steps",
            "No typed denominator, unit or role/stage transition evidence exists for inference edges.",
            schema_gap="argument_transition_semantics",
            remaining_debt=["D11", "D16"],
        )
