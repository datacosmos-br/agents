from __future__ import annotations

from pathlib import Path

import pytest

import agents_governance.temp as temp_module
from agents_governance.temp import require_repository_storage


def _repository(path: Path) -> Path:
    path.mkdir()
    return path


def _manifest(
    owner: Path,
    registered: str | Path,
) -> Path:
    path = owner / "config/storage.toml"
    path.parent.mkdir()
    path.write_text(
        f'version = 3\n\n[[repositories]]\npath = "{registered}"\n',
        encoding="utf-8",
    )
    return path


def _authority(tmp_path: Path) -> tuple[Path, Path, Path]:
    repository = _repository(tmp_path / "repository")
    path = _manifest(repository, "${CONFIG_DIR}/..")
    return repository, Path.home() / "tmp", path


def test_storage_derives_owner_and_defaults_without_redundant_inputs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repository = _repository(tmp_path / "repository")
    home = tmp_path / "home"
    home.mkdir()
    shell_temp = home / "tmp"
    shell_temp.mkdir()
    _manifest(repository, "${CONFIG_DIR}/..")
    monkeypatch.setenv("HOME", str(home))

    manifest = require_repository_storage(repository)

    assert manifest.repositories == (repository,)
    assert manifest.shell_temp == shell_temp


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("version = 3", "version = 2", "version"),
        ("version = 3", "version = 3\nunknown = 1", "fields must equal"),
        ("[[repositories]]", "", "fields must equal"),
        ("${CONFIG_DIR}", "${MISSING}", "unresolved"),
    ],
)
def test_manifest_rejects_first_schema_or_path_defect(
    tmp_path: Path,
    old: str,
    new: str,
    message: str,
) -> None:
    repository, _shell_temp, path = _authority(tmp_path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8"
    )

    with pytest.raises((TypeError, ValueError), match=message):
        require_repository_storage(repository)


def test_registered_repository_under_system_temp_is_accepted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    system_temp = tmp_path / "system-temp"
    system_temp.mkdir()
    repository = _repository(system_temp / "repository")
    _manifest(repository, "${CONFIG_DIR}/..")
    monkeypatch.setattr(temp_module, "SYSTEM_TEMP", system_temp)

    home = tmp_path / "home"
    home.mkdir()
    (home / "tmp").mkdir()
    monkeypatch.setenv("HOME", str(home))

    assert require_repository_storage(repository).repositories == (repository,)


def test_registered_repository_without_storage_config_is_rejected(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    with pytest.raises((ValueError, FileNotFoundError)):
        require_repository_storage(repository)


def test_registered_repository_without_git_is_accepted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    (home / "tmp").mkdir()
    system_temp = tmp_path / "system-temp"
    system_temp.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(temp_module, "SYSTEM_TEMP", system_temp)
    repository = tmp_path / "repository"
    repository.mkdir()
    _manifest(repository, "${CONFIG_DIR}/..")

    assert require_repository_storage(repository).repositories == (repository,)


def test_repository_storage_rejects_unregistered_root_and_first_residue(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path / "repository")
    other = _repository(tmp_path / "other")
    path = _manifest(repository, other)

    with pytest.raises(ValueError, match="absent"):
        require_repository_storage(repository)

    path.write_text(
        path.read_text(encoding="utf-8").replace(str(other), str(repository)),
        encoding="utf-8",
    )
    (repository / "$HOME").mkdir()
    (repository / ".archive").mkdir()
    with pytest.raises(ValueError, match=r"\$HOME"):
        require_repository_storage(repository)


def test_repository_storage_accepts_clean_registered_checkout(tmp_path: Path) -> None:
    repository, _shell_temp, _path = _authority(tmp_path)

    assert require_repository_storage(repository).repositories == (repository,)


def test_storage_owner_has_no_catch_finding_runner_gc_or_env_config() -> None:
    source = (
        Path(__file__).resolve().parents[1] / "src/agents_governance/temp.py"
    ).read_text(encoding="utf-8")

    assert "except " not in source
    assert "Finding" not in source
    assert "run_command" not in source
    assert "def gc" not in source
