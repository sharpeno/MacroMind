"""Small fail-closed contract checks, independent of future semantic validators."""

from pathlib import Path, PurePosixPath

from .models import ContractIntegrityReport, FrozenManifest
from .semantic_hash import calculate_file_sha256
from .version import ARTIFACTS


def verify_manifest_hashes(
    root: Path, manifest: FrozenManifest, report: ContractIntegrityReport
) -> None:
    # Historical manifest paths are provenance. Resolve only allowlisted basenames at the
    # caller's root, so relocated read-only contracts and isolated test copies work.
    names = [PurePosixPath(r["path"]).name for r in manifest.canonical_output_hashes]
    expected = set(ARTIFACTS) - {"freeze_manifest.json"}
    report.check("manifest_artifact_set", len(names) == len(set(names)) and set(names) == expected)
    for record, name in zip(manifest.canonical_output_hashes, names, strict=True):
        if name not in expected:
            continue
        path = root / name
        report.check(
            f"sha256:{name}", path.is_file() and calculate_file_sha256(path) == record["sha256"]
        )
