"""Typed public fixtures and the root test-verb execution guard."""

from __future__ import annotations

import os
import shutil
import tomllib
from pathlib import Path

import pytest

from agents_governance import GovernanceBundle


def pytest_configure(config: pytest.Config) -> None:
    """Reject every pytest path outside the root test verbs.

    ``make test`` runs with testmon against its default database;
    ``make test-full`` disables its plugin, so the optional plugin flag is absent.
    """

    mode = os.environ.get("TESTMON_MODE")
    if mode not in {"full", "incremental"}:
        raise pytest.UsageError(
            "tests must run through `make test` or `make test-full`"
        )
    incremental = mode == "incremental"
    if config.pluginmanager.hasplugin("pytest-testmon") is not incremental:
        raise pytest.UsageError(f"testmon plugin is not canonical for {mode}")
    if bool(config.getoption("testmon", default=False)) is not incremental:
        raise pytest.UsageError(f"testmon activation is not canonical for {mode}")


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
    inputs = configuration["tool"]["hatch"]["build"]["targets"]["wheel"][
        "force-include"
    ]
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
