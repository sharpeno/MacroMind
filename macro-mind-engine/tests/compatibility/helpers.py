from copy import deepcopy


def legacy(objects=None, ma1=False):
    value = {
        "02_SOURCES": [],
        "08_CLAIMS": objects
        if objects is not None
        else [{"claim_id": "c", "statement": "Recorded statement"}],
        "12_STRUCTURAL_PROCESSES": [],
        "18_ARGUMENTS": [],
    }
    if ma1:
        value["ma1_migration"] = {"schema_version": "V0.3.1-MA.1", "human_acceptance": True}
    return deepcopy(value)


def canonical(result, kind):
    return [o for o in result.canonical_bundle["objects"] if o["object_type"] == kind]
