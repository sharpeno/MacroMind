import pytest
from macromind.audit import AuditInputArtifact, AuditNormalizer


@pytest.fixture
def artifact():
    def build(content, kind="validation_report", **kwargs):
        return AuditInputArtifact.from_content(
            content, artifact_type=kind, phase="1.4", component="test", **kwargs
        )

    return build


@pytest.fixture
def normalizer():
    return AuditNormalizer()
