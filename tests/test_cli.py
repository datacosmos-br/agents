from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

from agents_governance import provenance, resources
from agents_governance.cli import main

ROOT = Path(__file__).resolve().parents[1]
VERBS = ("help", "doctor", "check", "sync", "evaluate", "secure", "clean", "live")


def _invoke(monkeypatch: pytest.MonkeyPatch, *arguments: str) -> None:
    monkeypatch.setattr(sys, "argv", ["agentsctl", *arguments])
    main()


def test_help_is_the_complete_optionless_surface(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _invoke(monkeypatch, "help")

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == (
        "agentsctl\n"
        "  help\n"
        "  doctor\n"
        "  check\n"
        "  sync\n"
        "  evaluate\n"
        "  secure\n"
        "  clean\n"
        "  live\n"
    )


@pytest.mark.parametrize(
    "arguments",
    [(), ("--help",), ("check", "--json"), ("unknown",), ("help", "extra")],
)
def test_cli_rejects_every_non_single_verb_grammar(
    monkeypatch: pytest.MonkeyPatch, arguments: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError, match="exactly one optionless verb"):
        _invoke(monkeypatch, *arguments)


def test_cli_and_runtime_orchestrator_contain_no_exception_catches() -> None:
    for relative in (
        Path("src/agents_governance/cli.py"),
        Path("src/agents_governance/runtime.py"),
    ):
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, (ast.Try, ast.TryStar)) for node in ast.walk(tree)
        )


def test_live_missing_environment_escapes_with_raw_traceback() -> None:
    environment = dict(os.environ)
    environment.pop("CLIPROXY_API_KEY", None)
    environment.pop("COPILOT_PROVIDER_API_KEY", None)

    result = subprocess.run(
        [sys.executable, "-m", "agents_governance.cli", "live"],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "Traceback (most recent call last)" in result.stderr
    assert "ValueError" in result.stderr
    assert "CLIPROXY_API_KEY" in result.stderr


def test_agentsctl_is_the_only_packaged_console_script() -> None:
    scripts = (
        (ROOT / "pyproject.toml")
        .read_text(encoding="utf-8")
        .split("[project.scripts]", maxsplit=1)[1]
        .split("[", maxsplit=1)[0]
        .strip()
    )

    assert scripts == 'agentsctl = "agents_governance.cli:main"'


def test_makefile_never_imports_private_agent_runtime() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "from agents_governance" not in makefile
    assert "uv run python -c" not in makefile
    assert "APPLY" not in makefile


def test_resource_root_resolves_bundled_data() -> None:
    assert resources.resource_root() == ROOT


def test_provenance_resolves_version_and_source() -> None:
    assert provenance.version() == "0.2.0"
    assert provenance.source_url() is not None


def test_keyring_maintenance_runtime_is_extinct() -> None:
    assert not (ROOT / "src/agents_governance/retired_environment.py").exists()
    runtime = (ROOT / "src/agents_governance/runtime.py").read_text(encoding="utf-8")
    assert all(
        term not in runtime
        for term in ("env-keyring", "environment-d-loader", "RetiredEnvironment")
    )


def test_declared_verbs_are_unique() -> None:
    assert len(VERBS) == len(set(VERBS))
