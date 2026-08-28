from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from agents_governance import runtime
from agents_governance.security import (
    ScannerRoute,
    audit,
    inventory,
    validate_document,
)


def _report(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "docs" / "security" / "semgrep-triage.md"
    path.parent.mkdir(parents=True)
    path.write_text(body, encoding="utf-8")
    return path


def _repository(path: Path, files: dict[str, str]) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    for relative, content in files.items():
        destination = path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    return path


def _python_project(extra: dict[str, str] | None = None) -> dict[str, str]:
    files = {
        "pyproject.toml": (
            "[project]\n"
            'name = "example"\n'
            'version = "0.1.0"\n'
            "\n"
            "[tool.agents-governance.security]\n"
            'fixture-roots = ["evals"]\n'
        ),
        "uv.lock": "version = 1\n",
    }
    files.update(extra or {})
    return files


def test_complete_finding_is_accepted(tmp_path: Path) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\n## Findings\n\n### 1 · MEDIUM · `rule`\n\n**Decisão**: corrigido\n\n**Evidência**: `semgrep scan` retornou código 0 sem o achado.\n",
    )
    validate_document(path)


def test_empty_decision_fails_closed(tmp_path: Path) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**:\n",
    )
    with pytest.raises(ValueError, match="decision is missing or empty"):
        validate_document(path)


def test_risk_acceptance_is_not_a_closing_decision(tmp_path: Path) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**: risco-aceito\n\n**Evidência**: nenhuma\n",
    )
    with pytest.raises(ValueError, match="unsupported decision"):
        validate_document(path)


def test_missing_report_is_blocking(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="no docs/security"):
        audit((tmp_path,))


def test_symlinked_report_is_blocking(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    report = tmp_path / "docs" / "security" / "semgrep-triage.md"
    report.parent.mkdir(parents=True)
    report.symlink_to(outside)

    with pytest.raises(ValueError, match="physical file"):
        audit((tmp_path,))


def test_manual_ledger_reference_does_not_invalidate_security_evidence(
    tmp_path: Path,
) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\nLedger: manual\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**: corrigido\n\n**Evidência**: scanner retornou código 0.\n",
    )
    validate_document(path)


def test_inventory_maps_each_tracked_project_manifest_to_one_scanner_route(
    tmp_path: Path,
) -> None:
    repository = _repository(
        tmp_path / "repository",
        _python_project(
            {
                "evals/sample/pyproject.toml": "[project]\nname = 'fixture'\n",
                "evals/sample/uv.lock": "version = 1\n",
            }
        ),
    )

    routes = inventory((repository,))

    assert len(routes) == 1
    route = routes[0]
    assert route.manifest == repository / "pyproject.toml"
    assert route.scanner_input == repository / "uv.lock"
    assert route.command == (
        "snyk",
        "test",
        "--file=uv.lock",
        "--dev",
        "--severity-threshold=low",
    )


def test_inventory_ignores_untracked_manifests(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repository", _python_project())
    untracked = repository / "nested" / "package.json"
    untracked.parent.mkdir()
    untracked.write_text('{"name": "untracked"}\n', encoding="utf-8")

    routes = inventory((repository,))

    assert [route.manifest for route in routes] == [repository / "pyproject.toml"]


def test_inventory_rejects_a_tracked_manifest_without_a_scanner_route(
    tmp_path: Path,
) -> None:
    repository = _repository(
        tmp_path / "repository",
        _python_project({"nested/package.json": '{"name": "unsupported"}\n'}),
    )

    with pytest.raises(ValueError, match="has no scanner route"):
        inventory((repository,))


def test_secure_targets_the_invocation_repository_and_passes_validated_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    (project / ".git").mkdir()
    manifest = project / "pyproject.toml"
    scanner_input = project / "uv.lock"
    manifest.write_text("[project]\nname='target'\n", encoding="utf-8")
    scanner_input.write_text("version=1\n", encoding="utf-8")
    route = ScannerRoute(project, manifest, scanner_input)
    storage_roots: list[Path] = []
    inventory_roots: list[Path] = []
    calls: list[tuple[tuple[str, ...], Path, dict[str, str]]] = []

    def storage(root: Path) -> None:
        storage_roots.append(root)

    def security(root: Path) -> tuple[ScannerRoute, ...]:
        inventory_roots.append(root)
        return (route,)

    def run(
        command: tuple[str, ...],
        *,
        cwd: Path,
        env: dict[str, str],
        check: bool,
    ) -> None:
        assert check is True
        calls.append((command, cwd, env))

    monkeypatch.chdir(nested)
    monkeypatch.setenv("SNYK_TOKEN", "process-token")
    monkeypatch.setattr(runtime, "require_repository_storage", storage)
    monkeypatch.setattr(runtime, "_security", security)
    monkeypatch.setattr(runtime.shutil, "which", lambda name: f"/tools/{name}")
    monkeypatch.setattr(runtime.subprocess, "run", run)

    runtime.secure(Path("/installed/agents"))

    assert storage_roots == [project]
    assert inventory_roots == [project]
    assert [cwd for _command, cwd, _env in calls] == [project, project, project]
    assert all(environment["SNYK_TOKEN"] == "process-token" for *_, environment in calls)
    assert calls[-1][0] == route.command


def test_secure_rejects_missing_snyk_token_before_any_scanner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    monkeypatch.chdir(project)
    monkeypatch.delenv("SNYK_TOKEN", raising=False)
    monkeypatch.setattr(runtime, "require_repository_storage", lambda _root: None)
    monkeypatch.setattr(runtime, "_security", lambda _root: ())
    monkeypatch.setattr(runtime.shutil, "which", lambda name: f"/tools/{name}")

    def unexpected(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("scanner started before SNYK_TOKEN preflight")

    monkeypatch.setattr(runtime.subprocess, "run", unexpected)

    with pytest.raises(ValueError, match="SNYK_TOKEN"):
        runtime.secure(Path("/installed/agents"))
