import json
import subprocess
from pathlib import Path

import pytest

from agents_governance.cli import main
from agents_governance.temp import TempFinding


@pytest.fixture(autouse=True)
def explicit_storage_manifest(monkeypatch, tmp_path: Path) -> Path:
    manifest = tmp_path / "storage.toml"
    manifest.write_text(
        "version = 2\n"
        "repositories = []\n"
        "[policy]\n"
        f'shell_temp = "{tmp_path / "shell-tmp"}"\n'
        "shell_temp_max_bytes = 1073741824\n"
        "report_max_bytes = 10485760\n"
        "warning_bytes = 1073741824\n"
        "failure_bytes = 5368709120\n"
        "orphan_age_days = 7\n"
        "poll_seconds = 0.01\n"
        "termination_grace_seconds = 0.1\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("AGENTS_STORAGE_CONFIG", str(manifest))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return manifest


def _projection_authority(root: Path) -> Path:
    (root / "config").mkdir(parents=True)
    (root / "skills").mkdir()
    (root / "commands").mkdir()
    (root / "config" / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 500,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )
    (root / "config" / "projections.json").write_text(
        json.dumps(
            {
                "version": 3,
                "surfaces": {
                    "rules": {
                        "personal": {"entries": []},
                        "project_generic": {"entries": []},
                    },
                },
                "personal_targets": {},
                "projects": {
                    "skills_path": ".agents/skills",
                    "command_targets": {
                        "cursor": {
                            "path": ".cursor/commands",
                            "max_tokens": 100_000,
                        }
                    },
                    "rules_path": ".agents/rules",
                },
            }
        ),
        encoding="utf-8",
    )
    return root


def _git_project(root: Path) -> Path:
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def test_project_cli_requires_explicit_project_root(tmp_path: Path) -> None:
    authority = _projection_authority(tmp_path / "authority")

    assert (
        main(
            [
                "--root",
                str(authority),
                "project",
                "--scope",
                "projects",
                "--surface",
                "skills",
                "--check",
            ]
        )
        == 1
    )


def test_project_cli_accepts_repeatable_project_roots(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    authority = _projection_authority(tmp_path / "authority")
    first = _git_project(tmp_path / "first")
    second = _git_project(tmp_path / "second")

    assert (
        main(
            [
                "--root",
                str(authority),
                "project",
                "--scope",
                "projects",
                "--surface",
                "skills",
                "--project-root",
                str(first),
                "--project-root",
                str(second),
                "--apply",
            ]
        )
        == 0
    )
    assert "PASS: projections converged" in capsys.readouterr().out
    assert (first / ".agents" / "skills" / ".agents-governance.json").is_file()
    assert (second / ".agents" / "skills" / ".agents-governance.json").is_file()


def test_discover_projects_cli_requires_and_reports_explicit_roots(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    authority = _projection_authority(tmp_path / "authority")
    project = _git_project(tmp_path / "project")

    assert main(["--root", str(authority), "discover-projects"]) == 1
    assert (
        main(
            [
                "--root",
                str(authority),
                "discover-projects",
                "--project-root",
                str(project),
            ]
        )
        == 0
    )
    assert f"{project}\tcapabilities=none" in capsys.readouterr().out


def test_validate_skill_keeps_scoped_eval_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    authority = _projection_authority(tmp_path / "authority")
    skill = authority / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\n"
        "description: Validate examples when a scoped CLI check is requested.\n"
        "metadata:\n"
        '  aihub.tags: \'["provenance:agents-owned","updates:manual","usage:on-demand"]\'\n'
        "---\n# Example\n",
        encoding="utf-8",
    )
    tasks = authority / "evals" / "example" / "tasks"
    tasks.mkdir(parents=True)
    (tasks.parent / "eval.yaml").write_text(
        "skill: example\n"
        "config:\n"
        "  timeout_seconds: 300\n"
        "  required_skills: [example]\n"
        "  skill_directories: [../../skills/agent-wide/example]\n"
        "graders: []\n",
        encoding="utf-8",
    )

    assert main(["--root", str(authority), "validate", "--skill", "example"]) == 1
    assert "evals/example/eval.yaml: eval-grader" in capsys.readouterr().err


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


def test_temp_cli_rejects_invalid_manifest_before_starting_child(
    monkeypatch,
    tmp_path: Path,
    explicit_storage_manifest: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    proof = tmp_path / "child-started"
    monkeypatch.chdir(repository)
    rendered = explicit_storage_manifest.read_text(encoding="utf-8")
    explicit_storage_manifest.write_text(
        rendered.replace("repositories = []\n", "") + "repositories = []\n",
        encoding="utf-8",
    )

    assert main(["temp", "run", "--", "touch", str(proof)]) == 2
    assert not proof.exists()
    assert "storage schema mismatch" in capsys.readouterr().err


def test_temp_audit_is_repository_scoped_unless_global_is_requested(
    monkeypatch, tmp_path: Path
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    system_temp = tmp_path / "system-temp"
    system_temp.mkdir()
    (system_temp / "beads-circuit").mkdir()
    monkeypatch.setattr("agents_governance.cli.temp_global_findings", list)

    assert main(["--root", str(repository), "temp", "audit"]) == 0

    monkeypatch.setattr(
        "agents_governance.cli.temp_global_findings",
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
        json.dumps(
            {
                "dimensions": [{"name": "clarity", "score": 4}],
                "overall_score": 4,
                "summary": "Clear and complete.",
            }
        ),
        encoding="utf-8",
    )

    assert main(["waza-artifact", str(artifact)]) == 0

    artifact.write_text(
        json.dumps(
            {
                "dimensions": [{"name": "clarity", "score": 0}],
                "overall_score": 0,
                "summary": "Out of contract.",
            }
        ),
        encoding="utf-8",
    )
    assert main(["waza-artifact", str(artifact)]) == 1


def test_waza_artifact_accepts_only_fresh_owner_model_full_success(
    tmp_path: Path,
) -> None:
    (tmp_path / ".waza.yaml").write_text(
        "defaults:\n  model: owner-model\n", encoding="utf-8"
    )
    artifact = tmp_path / "run.json"
    payload = {
        "schemaVersion": "1.2",
        "config": {"model_id": "owner-model"},
        "summary": {
            "total_tests": 1,
            "succeeded": 1,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        },
        "tasks": [
            {
                "status": "passed",
                "runs": [{"status": "passed", "error_msg": ""}],
            }
        ],
    }
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--root", str(tmp_path), "waza-artifact", str(artifact)]) == 0

    payload["summary"] = {
        "total_tests": 1,
        "succeeded": 0,
        "failed": 1,
        "errors": 0,
        "skipped": 0,
    }
    payload["tasks"] = [
        {
            "status": "failed",
            "runs": [{"status": "failed", "error_msg": "grader failed"}],
        }
    ]
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--root", str(tmp_path), "waza-artifact", str(artifact)]) == 1


def test_waza_artifact_publishes_only_after_validation(tmp_path: Path) -> None:
    (tmp_path / ".waza.yaml").write_text(
        "defaults:\n  model: owner-model\n", encoding="utf-8"
    )
    output = tmp_path / "results"
    output.mkdir()
    candidate = output / ".results.unique.candidate"
    destination = output / "results.json"
    payload = {
        "schemaVersion": "1.2",
        "config": {"model_id": "owner-model"},
        "summary": {
            "total_tests": 1,
            "succeeded": 1,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        },
        "tasks": [
            {
                "status": "passed",
                "runs": [{"status": "passed", "error_msg": ""}],
            }
        ],
    }
    candidate.write_text(json.dumps(payload), encoding="utf-8")

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "waza-artifact",
                str(candidate),
                "--publish",
                str(destination),
            ]
        )
        == 0
    )
    assert destination.is_file()
    assert not candidate.exists()

    invalid = output / ".invalid.unique.candidate"
    invalid.write_text("{}\n", encoding="utf-8")
    destination.unlink()
    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "waza-artifact",
                str(invalid),
                "--publish",
                str(destination),
            ]
        )
        == 1
    )
    assert invalid.is_file()
    assert not destination.exists()


def test_waza_model_catalog_requires_exactly_the_owner_model(tmp_path: Path) -> None:
    (tmp_path / ".waza.yaml").write_text(
        "defaults:\n  model: owner-model\n", encoding="utf-8"
    )
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps({"data": [{"id": "owner-model", "object": "model"}]}),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "waza-model-catalog", str(catalog)]) == 0

    catalog.write_text(
        json.dumps({"data": [{"id": "owner-model"}, {"id": "alternate"}]}),
        encoding="utf-8",
    )
    assert main(["--root", str(tmp_path), "waza-model-catalog", str(catalog)]) == 1


def test_waza_owner_failures_stop_at_the_cli_boundary(capsys, tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path), "waza-config", "--model"]) == 2
    config_error = capsys.readouterr()
    assert config_error.out == ""
    assert "FAIL: Waza configuration" in config_error.err

    assert main(["--root", str(tmp_path), "waza-preflight"]) == 2
    preflight_error = capsys.readouterr()
    assert preflight_error.out == ""
    assert "FAIL: Waza preflight" in preflight_error.err


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


def test_description_check_fails_on_drift_and_apply_requires_authored_rewrite(
    tmp_path: Path,
) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "project-wide" / "review"
    skill.mkdir(parents=True)
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 500,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )
    skill_file = skill / "SKILL.md"
    original = (
        "---\nname: review\ndescription: Use this skill for detailed reviews.\n"
        "metadata:\n"
        '  aihub.tags: \'["provenance:agents-owned","updates:manual","usage:on-demand"]\'\n'
        "---\n# Review\n"
    )
    skill_file.write_text(
        original,
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "descriptions"]) == 1
    assert main(["--root", str(tmp_path), "descriptions", "--apply"]) == 2
    assert skill_file.read_text(encoding="utf-8") == original


def test_normalize_check_fails_on_router_budget_drift(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "project-wide" / "large"
    skill.mkdir(parents=True)
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 20,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )
    (skill / "SKILL.md").write_text(
        "---\nname: large\n"
        "description: Route large procedures when detailed execution is required.\n"
        "metadata:\n"
        '  aihub.tags: \'["provenance:agents-owned","updates:manual","usage:router"]\'\n'
        "---\n# Large\n\n" + ("Detailed routing procedure. " * 100),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "normalize"]) == 1
