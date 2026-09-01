from __future__ import annotations

import importlib.util
import sqlite3
import stat
from pathlib import Path
from types import ModuleType

import pytest


def _module() -> ModuleType:
    path = (
        Path(__file__).parents[1]
        / "skills/agent-wide/personal/opencode-session-handoff/scripts"
        / "export_session_snapshot.py"
    )
    spec = importlib.util.spec_from_file_location("opencode_session_handoff", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _database(root: Path) -> None:
    with sqlite3.connect(root / "opencode.db") as database:
        database.executescript(
            """
            CREATE TABLE session (
                id TEXT, project_id TEXT, parent_id TEXT, directory TEXT,
                title TEXT, version TEXT, agent TEXT, model TEXT,
                time_created INTEGER, time_updated INTEGER
            );
            CREATE TABLE todo (
                session_id TEXT, position INTEGER, status TEXT, priority TEXT,
                content TEXT, time_created INTEGER, time_updated INTEGER
            );
            CREATE TABLE message (
                id TEXT, session_id TEXT, time_created INTEGER,
                time_updated INTEGER, data TEXT
            );
            CREATE TABLE part (
                id TEXT, message_id TEXT, session_id TEXT, time_created INTEGER,
                time_updated INTEGER, data TEXT
            );
            """
        )


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


def test_private_write_and_handoff_redact_secrets(tmp_path: Path) -> None:
    module = _module()
    target = tmp_path / "private" / "handoff.md"
    module._atomic_private_write(target, "secret")

    assert stat.S_IMODE(target.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert module._redact({"token": "visible", "text": "Bearer abc123"}) == {
        "token": "[REDACTED]",
        "text": "Bearer [REDACTED]",
    }
