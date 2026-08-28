from __future__ import annotations

from pathlib import Path

import pytest

from agents_governance.cleanup import run_atomic_publications
from agents_governance.retired_environment import RetiredEnvironmentProjection


def _write(home: Path, relative: str, content: bytes) -> Path:
    destination = home / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    destination.chmod(0o755 if relative.startswith(".local/bin/") else 0o644)
    return destination


def test_retirement_removes_owned_artifacts_and_preserves_adjacent_content(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    loader = _write(home, ".local/bin/environment-d-loader", b"")
    bashrc = _write(
        home,
        ".bashrc",
        b'[[ -f "$HOME/.config/shell/env.sh" ]] && source '
        b'"$HOME/.config/shell/env.sh"\n\nkeep-this-line\n',
    )
    agents = _write(
        home,
        ".config/environment.d/40-agents.conf",
        b"# Non-sensitive agent configuration only. Credentials belong in GNOME "
        b"Keyring.\nBASH_ENV=${HOME}/.config/shell/env.sh\nKEEP=value\n",
    )
    project = _write(
        home,
        ".config/environment.d/projects/agent-tools.envrc",
        b"# Non-sensitive project environment. Secrets are injected by env-keyring.\n"
        b"export KEEP=value\n",
    )
    retirement = RetiredEnvironmentProjection(home)

    run_atomic_publications(retirement.publications())

    assert not loader.exists()
    assert bashrc.read_bytes() == b"keep-this-line\n"
    assert agents.read_bytes() == (
        b"# Non-sensitive agent configuration only. Required credentials come from "
        b"the invoking process environment.\nKEEP=value\n"
    )
    assert project.read_bytes() == (
        b"# Non-sensitive project environment. Required credentials come from the "
        b"invoking process environment.\nexport KEEP=value\n"
    )
    retirement.check()
    assert retirement.publications() == ()


def test_retirement_rejects_unknown_artifact_before_any_effect(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    agents = _write(
        home,
        ".config/environment.d/40-agents.conf",
        b"BASH_ENV=${HOME}/.config/shell/env.sh\nKEEP=value\n",
    )
    _write(home, ".local/bin/environment-d-loader", b"foreign implementation\n")

    with pytest.raises(RuntimeError, match="unrecognized retired environment"):
        RetiredEnvironmentProjection(home).publications()

    assert agents.read_bytes() == (
        b"BASH_ENV=${HOME}/.config/shell/env.sh\nKEEP=value\n"
    )
    assert not tuple(home.glob(".agents-retired-environment.*"))


def test_retirement_detects_change_between_preflight_and_publish(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    loader = _write(home, ".local/bin/environment-d-loader", b"")
    publication = RetiredEnvironmentProjection(home).publications()[0]
    prepared = publication.prepare()
    loader.write_bytes(b"concurrent replacement\n")

    try:
        with pytest.raises(RuntimeError, match="changed after preflight"):
            prepared.publish()
    finally:
        prepared.cleanup()

    assert loader.read_bytes() == b"concurrent replacement\n"
    assert not tuple(home.glob(".agents-retired-environment.*"))


def test_check_rejects_retired_environment_residue(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    _write(home, ".local/bin/environment-d-loader", b"")

    with pytest.raises(RuntimeError, match="retired environment residue"):
        RetiredEnvironmentProjection(home).check()


def test_prepare_failure_removes_stage_and_preserves_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    bashrc = _write(
        home,
        ".bashrc",
        b'[[ -f "$HOME/.config/shell/env.sh" ]] && source '
        b'"$HOME/.config/shell/env.sh"\n\nkeep-this-line\n',
    )
    original = Path.write_bytes

    def fail_candidate(path: Path, data: bytes) -> int:
        if path.parent.name == "candidates":
            raise OSError("candidate write failed")
        return original(path, data)

    monkeypatch.setattr(Path, "write_bytes", fail_candidate)

    with pytest.raises(OSError, match="candidate write failed"):
        run_atomic_publications(RetiredEnvironmentProjection(home).publications())

    assert bashrc.read_bytes().endswith(b"keep-this-line\n")
    assert not tuple(home.glob(".agents-retired-environment.*"))


def test_publish_failure_rolls_back_every_changed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    bashrc_content = (
        b'[[ -f "$HOME/.config/shell/env.sh" ]] && source '
        b'"$HOME/.config/shell/env.sh"\n\nkeep-this-line\n'
    )
    agents_content = b"BASH_ENV=${HOME}/.config/shell/env.sh\nKEEP=value\n"
    bashrc = _write(home, ".bashrc", bashrc_content)
    agents = _write(
        home,
        ".config/environment.d/40-agents.conf",
        agents_content,
    )
    original = Path.replace

    def fail_second_candidate(path: Path, target: Path) -> Path:
        if path.parent.name == "candidates" and path.name == "1":
            raise OSError("second publication failed")
        return original(path, target)

    monkeypatch.setattr(Path, "replace", fail_second_candidate)

    with pytest.raises(OSError, match="second publication failed"):
        run_atomic_publications(RetiredEnvironmentProjection(home).publications())

    assert bashrc.read_bytes() == bashrc_content
    assert agents.read_bytes() == agents_content
    assert not tuple(home.glob(".agents-retired-environment.*"))
