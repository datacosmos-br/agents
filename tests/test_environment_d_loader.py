"""The global shell bootstrap must stay non-secret and deterministic."""

import runpy
from pathlib import Path
from typing import Any

import pytest


def _loader_namespace() -> dict[str, Any]:
    root = Path(__file__).parents[1]
    return runpy.run_path(str(root / "bin" / "environment-d-loader"))


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
