from __future__ import annotations

import tomllib
from pathlib import Path


def test_published_package_bundles_approval_authority() -> None:
    manifest = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    wheel = manifest["tool"]["hatch"]["build"]["targets"]["wheel"]
    force_include = wheel["force-include"]
    sdist_include = manifest["tool"]["hatch"]["build"]["targets"]["sdist"][
        "only-include"
    ]

    assert force_include["docs/adr"] == "agents_governance/_data/docs/adr"
    assert (
        force_include["docs/execution/master-v7"]
        == "agents_governance/_data/docs/execution/master-v7"
    )
    assert (
        force_include["docs/security/security-triage.md"]
        == "agents_governance/_data/docs/security/security-triage.md"
    )
    assert "docs/adr" in sdist_include
    assert "docs/execution/master-v7" in sdist_include
    assert "docs/security/security-triage.md" in sdist_include
