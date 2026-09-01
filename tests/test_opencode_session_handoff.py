from __future__ import annotations

import importlib.util
import json
import stat
import subprocess
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


def _snapshot() -> dict[str, object]:
    return {
        "schema_version": 1,
        "session": [
            {
                "id": "ses_example",
                "title": "Recovery",
                "directory": "/workspace/project",
                "agent": "build",
                "model": "model",
                "time_updated": 2,
            }
        ],
        "todos": [{"position": 1, "content": "Phase B", "status": "pending"}],
        "messages": [
            {
                "id": "msg_1",
                "data": {"role": "assistant", "token": "raw-secret"},
            }
        ],
        "parts": [
            {
                "id": "part_1",
                "message_id": "msg_1",
                "data": {"type": "text", "text": "Bearer visible-secret"},
            }
        ],
    }


def test_snapshot_uses_allowlisted_opencode_db_queries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    queries: list[str] = []

    def query(sql: str) -> list[dict[str, object]]:
        queries.append(sql)
        if sql.startswith("PRAGMA"):
            table = sql.removeprefix("PRAGMA table_info(").removesuffix(")")
            return [{"name": column} for column in module.TABLE_COLUMNS[table]]
        if "FROM session" in sql:
            return [{"id": "ses_example"}]
        if "FROM todo" in sql:
            return []
        return [{"id": "row", "message_id": "msg_1", "data": '{"type":"text"}'}]

    monkeypatch.setattr(module, "_query", query)

    snapshot = module._snapshot("ses_example")

    assert snapshot["session"] == [{"id": "ses_example"}]
    assert any("FROM message WHERE session_id='ses_example'" in sql for sql in queries)
    assert any("FROM part WHERE session_id='ses_example'" in sql for sql in queries)
    assert all("credential" not in sql.lower() for sql in queries)


def test_schema_validation_fails_closed_on_missing_column(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    def query(sql: str) -> list[dict[str, object]]:
        table = sql.removeprefix("PRAGMA table_info(").removesuffix(")")
        columns = set(module.TABLE_COLUMNS[table])
        if table == "todo":
            columns.remove("content")
        return [{"name": column} for column in columns]

    monkeypatch.setattr(module, "_query", query)

    with pytest.raises(ValueError, match="OpenCode todo schema is missing: content"):
        module._validate_schema()


def test_invalid_native_export_publishes_private_evidence_and_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    destination = tmp_path / "handoff"
    monkeypatch.setattr(
        module,
        "_completed",
        lambda *_args: subprocess.CompletedProcess(
            args=("opencode", "export"),
            returncode=0,
            stdout='{"truncated":',
            stderr="provider 401 token=visible-secret",
        ),
    )
    monkeypatch.setattr(module, "_snapshot", lambda _session_id: _snapshot())

    assert module._export("ses_example", destination) == 2

    manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    handoff = (destination / "handoff.sanitised.md").read_text(encoding="utf-8")
    assert manifest["native_export"]["status"] == "invalid"
    assert manifest["native_export"]["exit_code"] == 0
    assert manifest["database_snapshot"]["messages"] == 1
    assert "raw-secret" not in handoff
    assert "visible-secret" not in handoff
    assert "[REDACTED]" in handoff
    assert stat.S_IMODE(destination.stat().st_mode) == 0o700
    assert all(
        stat.S_IMODE(path.stat().st_mode) == 0o600 for path in destination.iterdir()
    )


def test_valid_native_export_succeeds_and_existing_destination_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    destination = tmp_path / "handoff"
    monkeypatch.setattr(
        module,
        "_completed",
        lambda *_args: subprocess.CompletedProcess(
            args=("opencode", "export"), returncode=0, stdout="{}", stderr=""
        ),
    )
    monkeypatch.setattr(module, "_snapshot", lambda _session_id: _snapshot())

    assert module._export("ses_example", destination) == 0
    with pytest.raises(FileExistsError, match="already exists"):
        module._export("ses_example", destination)
