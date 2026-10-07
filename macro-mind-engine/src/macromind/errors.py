"""Public error hierarchy. Invalid input is never repaired implicitly."""


class MacroMindError(Exception):
    pass


class ContractError(MacroMindError):
    pass


class ContractIntegrityError(ContractError):
    def __init__(self, report):
        self.report = report
        super().__init__("; ".join(report.errors))


class SchemaError(MacroMindError):
    pass


class RegistryError(MacroMindError):
    pass


class VersionError(MacroMindError):
    pass
