from .common import finding


def versions(s):
    for i, raw in enumerate(s.index.raw):
        bad = raw.get("schema_version") != "0.1.0" or raw.get("ontology_version") != "0.3"
        yield finding(
            s.index.raw_ref(i),
            "ERROR" if bad else "PASS",
            "/schema_version",
            "unsupported_schema_version" if bad else "Canonical version.",
            input_position=i,
        )


def shapes(s):
    for i in s.index.valid:
        yield finding(s.index.raw_ref(i))
    for i, errors in s.index.schema_errors.items():
        for error in errors:
            yield finding(
                s.index.raw_ref(i),
                "ERROR",
                "/" + "/".join(map(str, error["loc"])),
                error["message"],
                schema_error_type=error["type"],
                input_position=i,
            )
