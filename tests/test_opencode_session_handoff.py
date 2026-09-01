from __future__ import annotations

import importlib.util
import json
import sqlite3
import stat
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


def _module() -> ModuleType:
    path = (
        Path(__file__).parents[1]
        / "skills/agent-wide/personal/opencode-session-handoff/scripts/export_session_snapshot.py"
    )
    spec = importlib.util.spec_from_file_location("opencode_session_handoff", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _database(root: Path) -> None:
    with sqlite3.connect(root / "opencode.db") as database:
        database.executescript("""
            CREATE TABLE session (id TEXT, project_id TEXT, parent_id TEXT, directory TEXT, title TEXT, version TEXT, agent TEXT, model TEXT, time_created INTEGER, time_updated INTEGER);
            CREATE TABLE todo (session_id TEXT, position INTEGER, status TEXT, priority TEXT, content TEXT, time_created INTEGER, time_updated INTEGER);
            CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, time_updated INTEGER, data TEXT);
            CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, time_created INTEGER, time_updated INTEGER, data TEXT);
        """)


def _snapshot() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "session": [
            {
                "id": "ses_example",
                "title": "Recovery",
                "directory": "/workspace",
                "agent": "build",
                "model": "model",
                "time_updated": 2,
            }
        ],
        "todos": [{"position": 1, "content": "Phase B", "status": "pending"}],
        "messages": [
            {"id": "msg_1", "data": {"role": "assistant", "token": "raw-secret"}}
        ],
        "parts": [
            {
                "id": "part_1",
                "message_id": "msg_1",
                "data": {"type": "text", "text": "Bearer visible-secret"},
            }
        ],
    }


def test_database_is_schema_allowlisted_and_query_only(tmp_path: Path) -> None:
    module = _module()
    _database(tmp_path)
    with module._database(tmp_path) as database:
        assert database.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            database.execute("INSERT INTO session (id) VALUES ('ses_write')")


def test_database_rejects_missing_allowlisted_column(tmp_path: Path) -> None:
    module = _module()
    _database(tmp_path)
    with sqlite3.connect(tmp_path / "opencode.db") as database:
        database.execute("ALTER TABLE todo DROP COLUMN content")
    with pytest.raises(ValueError, match="OpenCode todo schema is missing: content"):
        module._database(tmp_path)


def _stub_native(
    monkeypatch: pytest.MonkeyPatch,
    module: ModuleType,
    stdout: bytes,
    stderr: bytes,
    returncode: int = 0,
) -> None:
    def run(*_args: object, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        kwargs["stdout"].write(stdout)
        kwargs["stderr"].write(stderr)
        return subprocess.CompletedProcess(
            args=("opencode", "export"), returncode=returncode
        )

    monkeypatch.setattr(module.subprocess, "run", run)


def test_invalid_native_export_publishes_private_evidence_and_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    destination = tmp_path / "handoff"
    _stub_native(monkeypatch, module, b'{"truncated":', b"provider 401 token=secret")
    monkeypatch.setattr(module, "_data_root", lambda: tmp_path)
    monkeypatch.setattr(module, "_snapshot", lambda _session_id, _root: _snapshot())
    assert module._export("ses_example", destination) == 2
    manifest = json.loads((destination / "manifest.json").read_text())
    handoff = (destination / "handoff.sanitised.md").read_text()
    assert manifest["native_export"]["status"] == "invalid"
    assert "raw-secret" not in handoff and "visible-secret" not in handoff
    assert stat.S_IMODE(destination.stat().st_mode) == 0o700
    assert all(
        stat.S_IMODE(path.stat().st_mode) == 0o600 for path in destination.iterdir()
    )


def test_valid_native_export_succeeds_and_existing_destination_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    destination = tmp_path / "handoff"
    _stub_native(monkeypatch, module, b"{}", b"")
    monkeypatch.setattr(module, "_data_root", lambda: tmp_path)
    monkeypatch.setattr(module, "_snapshot", lambda _session_id, _root: _snapshot())
    assert module._export("ses_example", destination) == 0
    with pytest.raises(FileExistsError, match="already exists"):
        module._export("ses_example", destination)


def test_native_failure_is_published_and_propagated_without_database_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    destination = tmp_path / "handoff"
    _stub_native(monkeypatch, module, b"partial", b"provider failed", returncode=7)
    monkeypatch.setattr(
        module,
        "_snapshot",
        lambda *_args: pytest.fail("database must not replace the first failure"),
    )

    assert module._export("ses_example", destination) == 7
    manifest = json.loads((destination / "manifest.json").read_text())
    assert manifest["native_export"]["exit_code"] == 7
    assert manifest["database_snapshot"] is None
    assert (
        destination / "native-export.invalid.private.log"
    ).read_bytes() == b"partial"
    assert (
        destination / "native-export.stderr.private.log"
    ).read_bytes() == b"provider failed"


def test_existing_output_parent_permissions_are_never_mutated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    parent = tmp_path / "foreign-parent"
    parent.mkdir(mode=0o755)
    parent.chmod(0o755)
    _stub_native(monkeypatch, module, b"{}", b"")

    with pytest.raises(PermissionError, match="private mode 0700"):
        module._export("ses_example", parent / "handoff")

    assert stat.S_IMODE(parent.stat().st_mode) == 0o755


def test_cleanup_failure_is_attached_without_masking_primary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    destination = tmp_path / "handoff"
    _stub_native(monkeypatch, module, b"{}", b"")
    monkeypatch.setattr(module, "_data_root", lambda: tmp_path)
    monkeypatch.setattr(
        module, "_snapshot", lambda *_args: (_ for _ in ()).throw(ValueError("primary"))
    )
    monkeypatch.setattr(
        module.shutil,
        "rmtree",
        lambda *_args: (_ for _ in ()).throw(OSError("cleanup")),
    )

    with pytest.raises(ValueError, match="primary") as raised:
        module._export("ses_example", destination)

    assert any("cleanup" in note for note in raised.value.__notes__)
