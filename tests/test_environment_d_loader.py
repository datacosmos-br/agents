"""The global shell bootstrap must stay non-secret and deterministic."""

import runpy
from pathlib import Path
from typing import Any

import pytest


def _loader_namespace() -> dict[str, Any]:
    namespace = runpy.run_module("agents_governance.environment_loader")
    namespace["shell_environment"] = lambda: {}
    return namespace


def test_loader_is_a_packaged_console_script_without_loose_launcher() -> None:
    root = Path(__file__).parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")

    assert (
        'environment-d-loader = "agents_governance.environment_loader:main"'
        in pyproject
    )
    assert not (root / "bin" / "environment-d-loader").exists()


def test_bootstrap_does_not_query_the_keyring(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    namespace = _loader_namespace()
    emit_bootstrap = namespace["emit_bootstrap"]
    assert callable(emit_bootstrap)
    empty = tmp_path / "environment.d"
    secrets = empty / "secrets"
    secrets.mkdir(parents=True)
    (secrets / "profiles.toml").write_text(
        "version = 1\nprofiles = {}\n", encoding="utf-8"
    )
    emit_bootstrap.__globals__["ENV_ROOT"] = empty

    emit_bootstrap("bash", False)

    output = capsys.readouterr().out
    assert "GITHUB_TOKEN" not in output
    assert "env-keyring" not in output


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_bootstrap_clears_canonical_and_aliased_secrets(
    shell: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    namespace = _loader_namespace()
    emit_bootstrap = namespace["emit_bootstrap"]
    assert callable(emit_bootstrap)
    environment = tmp_path / "environment.d"
    secrets = environment / "secrets"
    secrets.mkdir(parents=True)
    (secrets / "profiles.toml").write_text(
        """version = 1
[profiles.github]
variables = ["GITHUB_TOKEN"]
aliases = { GH_TOKEN = "GITHUB_TOKEN", MISE_GITHUB_TOKEN = "GITHUB_TOKEN" }
""",
        encoding="utf-8",
    )
    emit_bootstrap.__globals__["ENV_ROOT"] = environment

    emit_bootstrap(shell, False)

    output = capsys.readouterr().out
    for name in ("GITHUB_TOKEN", "GH_TOKEN", "MISE_GITHUB_TOKEN"):
        assert name in output


@pytest.mark.parametrize(
    ("shell", "prefix"),
    (("bash", "export"), ("zsh", "export"), ("fish", "set -gx")),
)
def test_storage_owner_is_materialized_equally_for_every_shell(
    shell: str,
    prefix: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    namespace = _loader_namespace()
    namespace["ENV_ROOT"] = tmp_path / "environment.d"
    namespace["ENV_ROOT"].mkdir()
    namespace["shell_environment"] = lambda: {
        "TMPDIR": "/home/test/tmp",
        "GOTMPDIR": "/home/test/tmp",
        "GOCACHE": "/home/test/.cache/go-build",
    }

    namespace["emit_environment"](shell)

    output = capsys.readouterr().out
    assert f"{prefix} TMPDIR" in output
    assert "/home/test/tmp" in output
    assert f"{prefix} GOTMPDIR" in output
    assert f"{prefix} GOCACHE" in output


def test_storage_projection_drift_fails_loudly() -> None:
    namespace = _loader_namespace()
    namespace["shell_environment"] = lambda: {"TMPDIR": "/owner/tmp"}

    with pytest.raises(ValueError, match="storage projection differs"):
        namespace["materialize_storage"]({"TMPDIR": "/stale/tmp"})


def test_generic_validator_rejects_plaintext_secrets_and_system_tmp(
    tmp_path: Path,
) -> None:
    namespace = _loader_namespace()
    validate_environment = namespace["validate_environment"]
    assert callable(validate_environment)
    environment = tmp_path / "environment.d"
    shell = environment / "shell"
    shell.mkdir(parents=True)
    (shell / "aliases.toml").write_text("[aliases]\n", encoding="utf-8")
    (shell / "completions.toml").write_text(
        "[bash]\nsource=[]\n[zsh]\nsource=[]\n[fish]\nsource=[]\n",
        encoding="utf-8",
    )
    config = environment / "10-local.conf"
    config.write_text("ANY_API_KEY=plaintext\nTMPDIR=/tmp\n", encoding="utf-8")
    validate_environment.__globals__["ENV_ROOT"] = environment

    with pytest.raises(ValueError, match="secret-like variables"):
        validate_environment()


def test_noninteractive_bootstrap_preserves_explicit_parent_path(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    namespace = _loader_namespace()
    emit_bootstrap = namespace["emit_bootstrap"]
    assert callable(emit_bootstrap)
    environment = tmp_path / "environment.d"
    secrets = environment / "secrets"
    secrets.mkdir(parents=True)
    (secrets / "profiles.toml").write_text(
        "version = 1\nprofiles = {}\n", encoding="utf-8"
    )
    (environment / "60-path.conf").write_text(
        "PATH=/canonical/bin:/usr/bin\nEDITOR=nvim\n", encoding="utf-8"
    )
    emit_bootstrap.__globals__["ENV_ROOT"] = environment

    emit_bootstrap("bash", False)

    output = capsys.readouterr().out
    assert "export PATH=" not in output
    assert "export EDITOR=nvim" in output


def test_interactive_bootstrap_emits_canonical_path(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    namespace = _loader_namespace()
    emit_bootstrap = namespace["emit_bootstrap"]
    assert callable(emit_bootstrap)
    environment = tmp_path / "environment.d"
    shell = environment / "shell"
    secrets = environment / "secrets"
    shell.mkdir(parents=True)
    secrets.mkdir()
    (secrets / "profiles.toml").write_text(
        "version = 1\nprofiles = {}\n", encoding="utf-8"
    )
    (environment / "60-path.conf").write_text(
        "PATH=/canonical/bin:/usr/bin\n", encoding="utf-8"
    )
    (shell / "aliases.toml").write_text("[aliases]\n", encoding="utf-8")
    (shell / "completions.toml").write_text("[bash]\nsource=[]\n", encoding="utf-8")
    emit_bootstrap.__globals__["ENV_ROOT"] = environment

    emit_bootstrap("bash", True)

    assert "export PATH=/canonical/bin:/usr/bin" in capsys.readouterr().out
