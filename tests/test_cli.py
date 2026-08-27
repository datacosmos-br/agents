import json
import subprocess
from pathlib import Path

import pytest

from agents_governance.cli import main
from agents_governance.temp import TempFinding


@pytest.fixture(autouse=True)
def explicit_storage_manifest(monkeypatch, tmp_path: Path) -> None:
    manifest = tmp_path / "storage.toml"
    manifest.write_text(
        "version = 1\n"
        "repositories = []\n"
        "[policy]\n"
        f'shell_temp = "{tmp_path / "shell-tmp"}"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("AGENTS_STORAGE_CONFIG", str(manifest))


def test_temp_run_uses_invocation_repository_not_agents_authority(
    monkeypatch, tmp_path: Path
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    monkeypatch.chdir(repository)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    assert main(["temp", "run", "--", "sh", "-c", "test -d .git"]) == 0


def test_temp_audit_is_repository_scoped_unless_global_is_requested(
    monkeypatch, tmp_path: Path
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    system_temp = tmp_path / "system-temp"
    system_temp.mkdir()
    (system_temp / "beads-circuit").mkdir()
    monkeypatch.setattr("agents_governance.cli.temp_findings", list)

    assert main(["--root", str(repository), "temp", "audit"]) == 0

    monkeypatch.setattr(
        "agents_governance.cli.temp_findings",
        lambda: [
            TempFinding(system_temp / "beads-circuit", "residue", "foreign residue")
        ],
    )
    assert main(["--root", str(repository), "temp", "audit", "--global"]) == 1


def test_waza_artifact_fails_closed_for_empty_or_invalid_output(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.touch()
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}\n", encoding="utf-8")

    assert main(["waza-artifact", str(empty)]) == 1
    assert main(["waza-artifact", str(invalid)]) == 1


def test_waza_artifact_accepts_scored_dimensions(tmp_path: Path) -> None:
    artifact = tmp_path / "quality.json"
    artifact.write_text(
        json.dumps({"dimensions": [{"name": "clarity", "score": 4}]}), encoding="utf-8"
    )

    assert main(["waza-artifact", str(artifact)]) == 0


def test_waza_coverage_requires_every_skill_fully_covered(tmp_path: Path) -> None:
    partial = tmp_path / "partial.json"
    partial.write_text(
        json.dumps({"total_skills": 2, "covered": 1, "partial": 1, "uncovered": 0}),
        encoding="utf-8",
    )
    complete = tmp_path / "complete.json"
    complete.write_text(
        json.dumps({"total_skills": 2, "covered": 2, "partial": 0, "uncovered": 0}),
        encoding="utf-8",
    )

    assert main(["waza-coverage", str(partial)]) == 1
    assert main(["waza-coverage", str(complete)]) == 0


def test_description_check_fails_on_drift_and_apply_repairs_it(
    tmp_path: Path,
) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "skills" / "review").mkdir(parents=True)
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "budgets": {
                    "router_tokens": 500,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
                "classification": [],
                "default": {
                    "class": "on_demand",
                    "provenance": "adopted",
                    "updates": "manual",
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "skills" / "review" / "SKILL.md").write_text(
        "---\nname: review\ndescription: Use this skill for detailed reviews.\n---\n# Review\n",
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "descriptions"]) == 1
    assert main(["--root", str(tmp_path), "descriptions", "--apply"]) == 0
    assert main(["--root", str(tmp_path), "descriptions"]) == 0


def test_normalize_check_fails_on_router_budget_drift(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "large"
    skill.mkdir(parents=True)
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "budgets": {
                    "router_tokens": 20,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
                "classification": [{"pattern": "large", "class": "router"}],
                "default": {
                    "class": "on_demand",
                    "provenance": "adopted",
                    "updates": "manual",
                },
            }
        ),
        encoding="utf-8",
    )
    (skill / "SKILL.md").write_text(
        "---\nname: large\ndescription: large, router\n---\n# Large\n\n"
        + ("Detailed routing procedure. " * 100),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "normalize"]) == 1
