"""Portable Beads activation contract for fresh linked worktrees."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import yaml


class TestsBeadsActivation:
    def test_generated_metadata_preserves_tracked_identity(self) -> None:
        """A checkout receives the same store and project identity as its owners."""

        root = Path(__file__).resolve().parents[1]
        spec = yaml.safe_load((root / "config/beads.yaml").read_text(encoding="utf-8"))
        identity = tomllib.loads(
            (root / ".beads/identity.toml").read_text(encoding="utf-8")
        )
        metadata = json.loads(
            (root / ".beads/metadata.json").read_text(encoding="utf-8")
        )
        assert metadata["dolt_database"] == spec["database"]
        assert metadata["project_id"] == identity["project"]["id"]
        assert metadata["dolt_mode"] == "server"
