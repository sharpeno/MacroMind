from macromind.errors import RegistryError


def check_identity_policies(entries, object_names) -> None:
    required = {"Actor", "Source", "SourceFamily", "Mechanism", "Indicator"}
    if not required <= {e.object_type for e in entries}:
        raise RegistryError("Required identity policy missing")
    if any(e.object_type not in object_names or e.automatic_merge for e in entries):
        raise RegistryError("Invalid identity policy; automatic merge is not supported")
