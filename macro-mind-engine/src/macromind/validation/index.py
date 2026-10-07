from collections import defaultdict

from pydantic import ValidationError

from macromind.schema.auxiliary import AUXILIARY_MODELS
from macromind.schema.core import CORE_MODELS

MODEL_TYPES = {**CORE_MODELS, **AUXILIARY_MODELS}


class ObjectIndex:
    """Duplicates and invalid targets are never silently resolved to an arbitrary object."""

    def __init__(self, objects, registered_types):
        self.raw = objects
        self.groups = defaultdict(list)
        self.valid = {}
        self.schema_errors = {}
        self.unsupported = {}
        self.unknown_types = {}
        for i, obj in enumerate(objects):
            identity = obj.get("id")
            if isinstance(identity, str):
                self.groups[identity].append(i)
            name = obj.get("object_type")
            if not isinstance(name, str) or name not in registered_types or name not in MODEL_TYPES:
                self.unknown_types[i] = name
                continue
            if obj.get("schema_version") != "0.1.0" or obj.get("ontology_version") != "0.3":
                self.unsupported[i] = {
                    "schema_version": obj.get("schema_version"),
                    "ontology_version": obj.get("ontology_version"),
                }
                continue
            try:
                model = MODEL_TYPES[name].model_validate(obj)
            except ValidationError as exc:
                self.schema_errors[i] = [
                    {"type": e["type"], "loc": list(e["loc"]), "message": e["msg"]}
                    for e in exc.errors()
                ]
            else:
                self.valid[i] = model
        self.objects = {m.id: m for i, m in self.valid.items() if len(self.groups[m.id]) == 1}

    def get(self, ref):
        return self.objects.get(ref)

    def of_type(self, *names):
        return sorted(
            (o for o in self.objects.values() if o.object_type in names), key=lambda o: o.id
        )

    def raw_ref(self, position):
        value = self.raw[position].get("id")
        return value if isinstance(value, str) else f"@input/{position}"

    def unresolved_reason(self, ref):
        if len(self.groups.get(ref, [])) > 1:
            return "ambiguous_duplicate_id"
        if ref in self.groups:
            return "invalid_target_schema"
        return "absent_from_bundle"
