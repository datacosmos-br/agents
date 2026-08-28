from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from agents_governance.security import (
    audit,
    inventory,
    main,
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
    assert validate_document(path) == ()


def test_empty_decision_fails_closed(tmp_path: Path) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**:\n",
    )
    assert [item.code for item in validate_document(path)] == ["missing-decision"]


def test_risk_acceptance_is_not_a_closing_decision(tmp_path: Path) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**: risco-aceito\n\n**Evidência**: nenhuma\n",
    )
    assert [item.code for item in validate_document(path)] == ["invalid-decision"]


def test_missing_report_is_blocking(tmp_path: Path) -> None:
    assert audit((tmp_path,))[0].code == "missing-report"


def test_manual_ledger_reference_does_not_invalidate_security_evidence(
    tmp_path: Path,
) -> None:
    path = _report(
        tmp_path,
        "# Triagem\n\nLedger: manual\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**: corrigido\n\n**Evidência**: scanner retornou código 0.\n",
    )
    assert validate_document(path) == ()


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

    result = inventory((repository,))

    assert result.findings == ()
    assert len(result.routes) == 1
    route = result.routes[0]
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

    result = inventory((repository,))

    assert result.findings == ()
    assert [route.manifest for route in result.routes] == [
        repository / "pyproject.toml"
    ]


def test_inventory_rejects_a_tracked_manifest_without_a_scanner_route(
    tmp_path: Path,
) -> None:
    repository = _repository(
        tmp_path / "repository",
        _python_project({"nested/package.json": '{"name": "unsupported"}\n'}),
    )

    result = inventory((repository,))

    assert [item.code for item in result.findings] == ["missing-scanner-route"]
    assert result.findings[0].path == str(repository / "nested" / "package.json")


def test_main_inventory_prints_deterministic_routes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repository = _repository(tmp_path / "repository", _python_project())

    assert main(["inventory", str(repository)]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == (
        f"{repository / 'pyproject.toml'}: snyk: uv.lock\n"
        "PASS: 1 tracked dependency manifest(s); 1 scanner route(s)\n"
    )


def test_main_snyk_executes_the_inventory_route_and_propagates_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository = _repository(tmp_path / "repository", _python_project())
    tools = tmp_path / "tools"
    tools.mkdir()
    log = tmp_path / "snyk.log"
    executable = tools / "snyk"
    executable.write_text(
        "#!/bin/sh\n"
        'printf "%s\\n" "$*" >> "$AGENTS_SECURITY_TEST_LOG"\n'
        'exit "$AGENTS_SECURITY_TEST_EXIT"\n',
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("AGENTS_SECURITY_TEST_LOG", str(log))
    monkeypatch.setenv("AGENTS_SECURITY_TEST_EXIT", "17")

    assert main(["snyk", str(repository)]) == 17

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "FAIL: snyk exited 17 for pyproject.toml" in captured.err
    assert log.read_text(encoding="utf-8") == (
        "test --file=uv.lock --dev --severity-threshold=low\n"
    )
