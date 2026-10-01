"""Portable Beads activation contract for fresh linked worktrees."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import yaml


class TestsBeadsActivation:
    def test_cli_generates_and_repairs_both_portable_outputs(
        self, tmp_path: Path
    ) -> None:
        """A new checkout receives the configured store and stable identity."""

        source = Path(__file__).resolve().parents[1]
        (tmp_path / "config").mkdir()
        (tmp_path / ".beads").mkdir()
        (tmp_path / "tools/templates").mkdir(parents=True)
        database = f"test_{uuid4().hex}"
        project_id = uuid4()
        workspace = yaml.safe_load(
            (source / "config/beads.yaml").read_text(encoding="utf-8")
        )
        workspace["database"] = database
        (tmp_path / "config/beads.yaml").write_text(
            yaml.safe_dump(workspace), encoding="utf-8"
        )
        shutil.copyfile(
            source / "config/beads-activation.yaml",
            tmp_path / "config/beads-activation.yaml",
        )
        (tmp_path / ".beads/identity.toml").write_text(
            f'[project]\nid = "{project_id}"\n', encoding="utf-8"
        )
        template = tmp_path / "tools/templates/agents.envrc"
        shutil.copyfile(source / "tools/templates/agents.envrc", template)
        command = (
            sys.executable,
            str(source / "tools/sync_beads_activation.py"),
            "--root",
            str(tmp_path),
        )

        subprocess.run(command, check=True, capture_output=True, text=True)
        metadata_path = tmp_path / ".beads/metadata.json"
        envrc_path = tmp_path / ".envrc"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        protocol = yaml.safe_load(
            (tmp_path / "config/beads-activation.yaml").read_text(encoding="utf-8")
        )
        assert metadata["backend"] == protocol["backend"]
        assert metadata["database"] == protocol["storage_database"]
        assert metadata["dolt_mode"] == protocol["dolt_mode"]
        assert metadata["dolt_database"] == database
        assert metadata["project_id"] == str(project_id)
        assert envrc_path.read_bytes() == template.read_bytes()

        metadata_path.write_text("stale\n", encoding="utf-8")
        envrc_path.write_text("stale\n", encoding="utf-8")
        subprocess.run(command, check=True, capture_output=True, text=True)
        assert json.loads(metadata_path.read_text(encoding="utf-8")) == metadata
        assert envrc_path.read_bytes() == template.read_bytes()
        before = (metadata_path.stat().st_mtime_ns, envrc_path.stat().st_mtime_ns)
        subprocess.run(command, check=True, capture_output=True, text=True)
        assert (
            metadata_path.stat().st_mtime_ns,
            envrc_path.stat().st_mtime_ns,
        ) == before

    def test_cli_rejects_invalid_identity_without_publishing(
        self, tmp_path: Path
    ) -> None:
        """An invalid tracked owner leaves no apparently usable activation."""

        source = Path(__file__).resolve().parents[1]
        (tmp_path / "config").mkdir()
        (tmp_path / ".beads").mkdir()
        shutil.copyfile(source / "config/beads.yaml", tmp_path / "config/beads.yaml")
        shutil.copyfile(
            source / "config/beads-activation.yaml",
            tmp_path / "config/beads-activation.yaml",
        )
        (tmp_path / ".beads/identity.toml").write_text(
            '[project]\nid = "invalid"\n', encoding="utf-8"
        )
        completed = subprocess.run(
            (
                sys.executable,
                str(source / "tools/sync_beads_activation.py"),
                "--root",
                str(tmp_path),
            ),
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode != 0
        assert "ValidationError" in completed.stderr
        assert not (tmp_path / ".beads/metadata.json").exists()
        assert not (tmp_path / ".envrc").exists()
