from .models import AdapterSpec


class CompatibilityAdapterRegistry:
    def __init__(self):
        self.specs = tuple(
            AdapterSpec(
                adapter_id="compat." + family.lower(),
                source_family=family,
                loss_profile=profile,
                implementation_module=module,
            )
            for family, profile, module in (
                (
                    "SUMMARY_ONLY_LEGACY",
                    "PARTIAL: raw summary only; reconstruction forbidden",
                    "macromind.compatibility.adapters.summary_only",
                ),
                (
                    "LEGACY_PRE_MA",
                    "PARTIAL/LOSSY_BUT_SAFE: missing semantics unknown or quarantined",
                    "macromind.compatibility.adapters.numbered",
                ),
                (
                    "V0_3_LEGACY",
                    "PARTIAL/LOSSY_BUT_SAFE: explicit fields only",
                    "macromind.compatibility.adapters.numbered",
                ),
                (
                    "MA1_COMPAT",
                    "Lossless only if every semantic field is representable; accepted history retained",
                    "macromind.compatibility.adapters.numbered",
                ),
                (
                    "CANONICAL_0_1",
                    "Canonical pass-through; unsupported shapes quarantined",
                    "macromind.compatibility.adapters.numbered",
                ),
            )
        )

    def select(self, detection, target_schema_version="0.1.0"):
        if detection.status not in ("EXACT", "STRONG"):
            return None
        return next(
            (
                s
                for s in self.specs
                if s.source_family == detection.family
                and s.target_schema_version == target_schema_version
            ),
            None,
        )

    def catalog(self):
        return [s.model_dump(mode="json") for s in self.specs]
