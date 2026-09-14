"""Typed public fixtures and mandatory pytest-testmon execution guard."""

from __future__ import annotations

import os
import shutil
import tomllib
from pathlib import Path

import pytest

from agents_governance import GovernanceBundle


def pytest_configure(config: pytest.Config) -> None:
    """Reject every pytest path that bypasses testmon or writes in the checkout."""

    if not config.getoption("testmon"):
        raise pytest.UsageError("tests must run through the Make pytest-testmon owner")
    configured = os.environ.get("TESTMON_DATAFILE")
    if configured is None or not configured.strip():
        raise pytest.UsageError("TESTMON_DATAFILE must select the shared cache")
    datafile = Path(configured).expanduser().resolve()
    repository = Path(config.rootpath).resolve()
    if datafile.is_relative_to(repository):
        raise pytest.UsageError("the testmon database must remain outside the checkout")


@pytest.fixture(scope="session")
def governance_bundle() -> GovernanceBundle:
    """Load the same immutable public facade used by every consumer."""

    return GovernanceBundle.load()


@pytest.fixture
def governance_source_fixture(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> Path:
    """Copy only the package's configured data inputs into a test-owned root."""
    repository = Path(__file__).resolve().parents[1]
    configuration = tomllib.loads((repository / "pyproject.toml").read_text())
    inputs = configuration["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    root = tmp_path / "bundle"
    root.mkdir()
    for relative in inputs:
        source = governance_bundle.root / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    return root
