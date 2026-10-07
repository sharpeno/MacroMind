"""Developer build step; YAML remains authoritative. Run before schema export."""

from pathlib import Path

from macromind.registry.enums import generate_python_enums

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    generate_python_enums(ROOT / "registries/v0_3", ROOT / "src/macromind/registry/_enums.py")
