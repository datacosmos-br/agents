"""Project this repository's portable Beads identity and direnv activation."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Literal
from uuid import UUID

import yaml
from pydantic import BaseModel, ConfigDict, Field


class BeadsSpec(BaseModel):
    """Tracked repository identity consumed by the generated activation."""

    model_config = ConfigDict(extra="forbid")

    version: Literal[1]
    workspace: str = Field(min_length=1)
    database: str = Field(min_length=1)
    issue_prefix: str = Field(min_length=1)


class ProjectIdentity(BaseModel):
    """Canonical project identifier minted by the selected Beads store."""

    model_config = ConfigDict(extra="forbid")

    id: UUID


class IdentityDocument(BaseModel):
    """Tracked Beads identity document."""

    model_config = ConfigDict(extra="forbid")

    project: ProjectIdentity


def project(root: Path) -> None:
    """Publish only byte changes after validating both tracked owners."""

    spec = BeadsSpec.model_validate(
        yaml.safe_load((root / "config/beads.yaml").read_text(encoding="utf-8"))
    )
    identity = IdentityDocument.model_validate(
        tomllib.loads((root / ".beads/identity.toml").read_text(encoding="utf-8"))
    )
    metadata = {
        "backend": "dolt",
        "database": "dolt",
        "dolt_database": spec.database,
        "dolt_mode": "server",
        "project_id": str(identity.project.id),
    }
    outputs = {
        root / ".beads/metadata.json": json.dumps(metadata, indent=2) + "\n",
        root / ".envrc": (root / "tools/templates/agents.envrc").read_text(
            encoding="utf-8"
        ),
    }
    for path, content in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
    print("Beads activation projected: metadata + direnv")


def main() -> None:
    project(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
