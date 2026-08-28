"""Waza online commands must receive credentials only through the keyring owner."""

import os
import runpy
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest


def _keyring_namespace() -> dict[str, Any]:
    root = Path(__file__).parents[1]
    return runpy.run_path(str(root / "bin" / "env-keyring"))


def test_waza_auth_uses_automatic_keyring_execution() -> None:
    """Prevent file scraping or ambient-secret fallbacks from returning."""
    root = Path(__file__).parents[1]
    config = (root / "config" / "waza.mk").read_text(encoding="utf-8")
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "env-keyring auto-exec" in config
    assert "agent:agents-waza" in config
    assert "CLIPROXY_AUTH_FILE" not in config
    assert "awk -F=" not in config
    assert "COPILOT_PROVIDER_API_KEY ?=" not in config
    assert "$(WAZA_ONLINE) quality" in makefile
    assert "$(WAZA_ONLINE) run" in makefile
    assert "$(WAZA_ONLINE) suggest" in makefile
    status_recipe = makefile.split("\nstatus:", maxsplit=1)[1].split(
        "\nmodels:", maxsplit=1
    )[0]
    assert 'models"\' && echo "  ok   cliproxy' in status_recipe
    assert 'models"\'; echo "  ok   cliproxy' not in status_recipe


def test_models_uses_the_canonical_online_waza_contract() -> None:
    """Model discovery must validate the real proxy catalog against its owner."""
    root = Path(__file__).parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    recipe = makefile.split("\nmodels:", maxsplit=1)[1].split("\nsetup:", maxsplit=1)[0]

    assert "COPILOT_PROVIDER_BASE_URL" in recipe
    assert "COPILOT_BASE_URL" not in recipe
    assert '"$$COPILOT_PROVIDER_BASE_URL/models"' in recipe
    assert "waza-model-catalog" in recipe
    assert "$(WAZA_ONLINE) models" not in recipe
    assert "$(WAZA_KEYRING_EXEC) waza models" not in recipe


def test_waza_model_is_resolved_only_from_the_project_owner() -> None:
    root = Path(__file__).parents[1]
    config = (root / "config" / "waza.mk").read_text(encoding="utf-8")
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "MODEL ?=" not in makefile
    assert "MODEL=" not in makefile
    assert "MODEL_ARG" not in config
    assert "WAZA_MODEL =" not in config
    assert "waza-config --model" in config
    assert 'COPILOT_MODEL="$$owner_model"' in config
    assert '--model "$$owner_model"' in config


def test_waza_results_use_unique_candidates_and_owner_publication() -> None:
    root = Path(__file__).parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "results.json.candidate" not in makefile
    assert "$$final.candidate" not in makefile
    assert makefile.count('mktemp "$$final.XXXXXX.candidate"') == 4
    assert makefile.count('waza-artifact "$$candidate" --publish "$$final"') == 4
    assert "agentsctl waza-preflight --model" not in makefile
    assert "agentsctl waza-preflight" in makefile
    coverage_recipe = makefile.split("\ncoverage:", maxsplit=1)[1].split(
        "\nrun:", maxsplit=1
    )[0]
    assert "trap" not in coverage_recipe
    assert 'mktemp "$$TMPDIR/coverage.XXXXXX.json"' in coverage_recipe
    gate_recipe = makefile.split("\ngate:", maxsplit=1)[1].split(
        "\ncompare:", maxsplit=1
    )[0]
    assert gate_recipe.count("agentsctl waza-artifact") == 2


def test_make_rejects_model_override_as_an_execution_interface() -> None:
    root = Path(__file__).parents[1]
    environment = {**os.environ, "COPILOT_MODEL": "ambient-alternate"}

    result = subprocess.run(
        [
            "make",
            "--no-print-directory",
            "-n",
            "run",
            "SKILL=fail-fast",
            "MODEL=command-line-alternate",
            "WAZA_MODEL=legacy-alternate",
            "RESULTS_DIR=../outside",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 0, result.stderr
    assert "command-line-alternate" not in result.stdout
    assert "legacy-alternate" not in result.stdout
    assert "ambient-alternate" not in result.stdout
    assert "../outside" not in result.stdout
    assert "results/latest/results.json" in result.stdout
    assert "waza-config --model" in result.stdout


def test_keyring_aliases_export_one_canonical_secret_under_declared_names(
    tmp_path: Path,
) -> None:
    """Aliases must reuse a declared secret without storing a duplicate."""
    manifest = tmp_path / "profiles.toml"
    manifest.write_text(
        """version = 1
[profiles.test]
variables = ["SOURCE_TOKEN"]
aliases = { CONSUMER_TOKEN = "SOURCE_TOKEN" }
""",
        encoding="utf-8",
    )
    namespace = _keyring_namespace()
    profile_config = namespace["profile_config"]
    fetch_all = namespace["fetch_all"]
    assert callable(profile_config)
    assert callable(fetch_all)
    profile_config.__globals__["MANIFEST"] = manifest
    fetch_all.__globals__["lookup"] = lambda _profile, _name: "secret-value"

    config = profile_config("test")
    exported = fetch_all("test", config)

    assert exported == {
        "SOURCE_TOKEN": "secret-value",
        "CONSUMER_TOKEN": "secret-value",
    }


def test_keyring_alias_rejects_an_undeclared_source(tmp_path: Path) -> None:
    """An alias cannot introduce a second secret source or implicit fallback."""
    manifest = tmp_path / "profiles.toml"
    manifest.write_text(
        """version = 1
[profiles.test]
variables = ["SOURCE_TOKEN"]
aliases = { CONSUMER_TOKEN = "MISSING_TOKEN" }
""",
        encoding="utf-8",
    )
    namespace = _keyring_namespace()
    profile_config = namespace["profile_config"]
    keyring_error = cast(type[Exception], namespace["KeyringError"])
    assert callable(profile_config)
    profile_config.__globals__["MANIFEST"] = manifest

    with pytest.raises(keyring_error, match="invalid aliases"):
        profile_config("test")


def test_remove_alias_clears_only_the_exact_legacy_record(tmp_path: Path) -> None:
    config_home = tmp_path / "config"
    manifest = config_home / "environment.d" / "secrets" / "profiles.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        """version = 1
[profiles.test]
variables = ["GITHUB_TOKEN"]
aliases = { GH_TOKEN = "GITHUB_TOKEN" }
""",
        encoding="utf-8",
    )
    commands = tmp_path / "commands"
    tools = tmp_path / "bin"
    tools.mkdir()
    secret_tool = tools / "secret-tool"
    secret_tool.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$@" > "$COMMAND_CAPTURE"\n',
        encoding="utf-8",
    )
    secret_tool.chmod(0o700)
    environment = {
        **os.environ,
        "COMMAND_CAPTURE": str(commands),
        "PATH": f"{tools}:{os.environ['PATH']}",
        "XDG_CONFIG_HOME": str(config_home),
        "XDG_STATE_HOME": str(tmp_path / "state"),
    }
    root = Path(__file__).parents[1]

    command = [
        str(root / "bin" / "env-keyring"),
        "remove",
        "--profile",
        "test",
        "--name",
        "GH_TOKEN",
    ]
    result = subprocess.run(
        [*command, "--yes"],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert commands.read_text(encoding="utf-8").splitlines() == [
        "clear",
        "application",
        "dev-environment",
        "profile",
        "test",
        "name",
        "GH_TOKEN",
    ]
    events = tmp_path / "state" / "env-keyring" / "events.jsonl"
    assert '"name": "GH_TOKEN"' in events.read_text(encoding="utf-8")

    commands.unlink()
    missing_confirmation = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    undeclared = subprocess.run(
        [*command[:-1], "UNDECLARED_TOKEN", "--yes"],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert missing_confirmation.returncode == 78
    assert undeclared.returncode == 78
    assert not commands.exists()


def test_shell_exports_fetch_only_explicit_ambient_values(tmp_path: Path) -> None:
    """Directory activation must not fetch or export generic GitHub tokens."""
    manifest = tmp_path / "profiles.toml"
    manifest.write_text(
        """version = 1
[profiles.test]
variables = ["GITHUB_TOKEN", "PROJECT_TOKEN"]
shell_variables = ["PROJECT_TOKEN"]
roots = ["${HOME}"]
""",
        encoding="utf-8",
    )
    namespace = _keyring_namespace()
    profile_config = namespace["profile_config"]
    fetch_shell = namespace["fetch_shell"]
    assert callable(profile_config)
    assert callable(fetch_shell)
    profile_config.__globals__["MANIFEST"] = manifest
    requested: list[str] = []

    def fake_lookup(_profile: str, name: str) -> str:
        requested.append(name)
        return f"secret-{name}"

    fetch_shell.__globals__["lookup"] = fake_lookup

    exported = fetch_shell("test", profile_config("test"))

    assert requested == ["PROJECT_TOKEN"]
    assert exported == {"PROJECT_TOKEN": "secret-PROJECT_TOKEN"}


def test_root_expansion_rejects_unknown_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = _keyring_namespace()
    expand_root = namespace["expand_root"]
    keyring_error = cast(type[Exception], namespace["KeyringError"])
    assert callable(expand_root)
    monkeypatch.setenv("HOME", "/home/test")

    assert expand_root("${HOME}/project") == Path("/home/test/project")
    with pytest.raises(keyring_error, match="unsupported root variable"):
        expand_root("${UNDECLARED}/project")
