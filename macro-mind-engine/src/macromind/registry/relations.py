from macromind.errors import RegistryError


def check_relations(entries, object_names) -> None:
    for entry in entries:
        if not set(entry.source_types + entry.target_types) <= set(object_names):
            raise RegistryError(f"Unknown relation endpoint: {entry.name}")
