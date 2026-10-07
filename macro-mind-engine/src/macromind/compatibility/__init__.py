from .detector import detect_legacy_format
from .engine import CompatibilityEngine
from .models import COMPATIBILITY_ADAPTER_VERSION, AdaptationResult, DetectionResult
from .registry import CompatibilityAdapterRegistry

__all__ = [
    "CompatibilityEngine",
    "CompatibilityAdapterRegistry",
    "detect_legacy_format",
    "AdaptationResult",
    "DetectionResult",
    "COMPATIBILITY_ADAPTER_VERSION",
]
