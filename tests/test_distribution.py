"""Distribution metadata tests for the MIRAGE alpha package."""

from importlib.metadata import metadata

import mirage


def test_public_version_is_pep_440_alpha() -> None:
    assert mirage.__version__ == "0.1.0a0"


def test_distribution_metadata_matches_registry_safe_identity() -> None:
    project_metadata = metadata("mirage-engineering")
    assert project_metadata["Name"] == "mirage-engineering"
    assert project_metadata["Version"] == mirage.__version__
