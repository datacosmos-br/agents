"""Project this repository's portable Beads identity and direnv activation."""

from __future__ import annotations

import tomllib
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal
from uuid import UUID

import yaml
from flext_core import m


class BeadsProject(m.FrozenModel):
    """Tracked workspace routing owned by the governance generator."""

    version: Literal[1] = m.Field(description="Beads project config format version")
    workspace: str = m.Field(min_length=1, description="Project workspace name")
    database: str = m.Field(min_length=1, description="Project Dolt database name")
    issue_prefix: str = m.Field(
        min_length=1, description="Project issue identifier prefix"
    )


class BeadsActivation(m.FrozenModel):
    """Tracked Beads protocol declaration for this standalone project."""

    backend: str = m.Field(min_length=1, description="Beads storage backend")
    storage_database: str = m.Field(
        min_length=1, description="Beads metadata storage identifier"
    )
    dolt_mode: str = m.Field(min_length=1, description="Dolt connection mode")


class BeadsProjectIdentity(m.FrozenModel):
    """Stable project identity published by Beads."""

    id: UUID = m.Field(description="Stable Beads project UUID")


class BeadsIdentityDocument(m.FrozenModel):
    """Tracked Beads identity document."""

    project: BeadsProjectIdentity = m.Field(description="Project identity")


class BeadsMetadata(m.FrozenModel):
    """Public Beads identity projected into every linked checkout."""

    backend: str = m.Field(description="Beads storage backend")
    database: str = m.Field(description="Beads metadata storage identifier")
    dolt_database: str = m.Field(description="Project Dolt database name")
    dolt_mode: str = m.Field(description="Dolt connection mode")
    project_id: str = m.Field(description="Stable Beads project UUID")


def project(root: Path) -> None:
    """Publish only byte changes after validating both tracked owners."""

    spec = BeadsProject.model_validate(
        yaml.safe_load((root / "config/beads.yaml").read_text(encoding="utf-8"))
    )
    activation = BeadsActivation.model_validate(
        yaml.safe_load(
            (root / "config/beads-activation.yaml").read_text(encoding="utf-8")
        )
    )
    identity = BeadsIdentityDocument.model_validate_strings(
        tomllib.loads((root / ".beads/identity.toml").read_text(encoding="utf-8"))
    )
    metadata = BeadsMetadata(
        backend=activation.backend,
        database=activation.storage_database,
        dolt_database=spec.database,
        dolt_mode=activation.dolt_mode,
        project_id=str(identity.project.id),
    )
    outputs = {
        root / ".beads/metadata.json": metadata.model_dump_json(indent=2) + "\n",
        root / ".envrc": (root / "tools/templates/agents.envrc").read_text(
            encoding="utf-8"
        ),
    }
    for path, content in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
    print("Beads activation projected: metadata + direnv")


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    arguments = parser.parse_args()
    project(arguments.root)


if __name__ == "__main__":
    main()
