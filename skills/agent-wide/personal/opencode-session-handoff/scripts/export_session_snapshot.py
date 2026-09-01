#!/usr/bin/env python3
"""Export one OpenCode session into a private, evidence-preserving handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SESSION_ID = re.compile(r"^ses_[A-Za-z0-9]+$")
SECRET_KEY = re.compile(
    r"(?:authorization|cookie|credential|password|secret|token|api[_-]?key)",
    re.IGNORECASE,
)
SECRET_TEXT = (
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)((?:set-)?cookie\s*[:=]\s*)[^\r\n]+"),
    re.compile(r"(?i)((?:api[_-]?key|token|password|secret)\s*[:=]\s*)\S+"),
)
TABLE_COLUMNS = {
    "session": frozenset(
        {
            "id",
            "project_id",
            "parent_id",
            "directory",
            "title",
            "version",
            "agent",
            "model",
            "time_created",
            "time_updated",
        }
    ),
    "todo": frozenset(
        {
            "session_id",
            "position",
            "status",
            "priority",
            "content",
            "time_created",
            "time_updated",
        }
    ),
    "message": frozenset(
        {"id", "session_id", "time_created", "time_updated", "data"}
    ),
    "part": frozenset(
        {"id", "message_id", "session_id", "time_created", "time_updated", "data"}
    ),
}


def _completed(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, capture_output=True, text=True)


def _run(*args: str) -> str:
    completed = _completed(*args)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed.stdout


def _query(sql: str) -> list[dict[str, Any]]:
    payload = json.loads(_run("opencode", "db", sql, "--format", "json"))
    if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
        raise TypeError("OpenCode database query did not return a JSON row list")
    return payload


def _validate_schema() -> None:
    for table, required in TABLE_COLUMNS.items():
        rows = _query(f"PRAGMA table_info({table})")
        actual = {str(row.get("name")) for row in rows}
        missing = required - actual
        if missing:
            raise ValueError(
                f"OpenCode {table} schema is missing: {', '.join(sorted(missing))}"
            )


def _decode_data(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decoded: list[dict[str, Any]] = []
    for row in rows:
        raw = row.get("data")
        if not isinstance(raw, str):
            raise TypeError("OpenCode data column is not JSON text")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TypeError("OpenCode data column is not a JSON object")
        decoded.append({**row, "data": data})
    return decoded


def _snapshot(session_id: str) -> dict[str, Any]:
    _validate_schema()
    quoted = f"'{session_id}'"
    session = _query(
        "SELECT id, project_id, parent_id, directory, title, version, agent, model, "
        f"time_created, time_updated FROM session WHERE id={quoted}"
    )
    if len(session) != 1:
        raise LookupError(f"expected exactly one OpenCode session for {session_id}")
    return {
        "schema_version": 1,
        "session": session,
        "todos": _query(
            "SELECT position, status, priority, content, time_created, time_updated "
            f"FROM todo WHERE session_id={quoted} ORDER BY position"
        ),
        "messages": _decode_data(
            _query(
                "SELECT id, time_created, time_updated, data FROM message "
                f"WHERE session_id={quoted} ORDER BY time_created, id"
            )
        ),
        "parts": _decode_data(
            _query(
                "SELECT id, message_id, time_created, time_updated, data FROM part "
                f"WHERE session_id={quoted} ORDER BY time_created, id"
            )
        ),
    }


def _redact(value: Any, key: str = "") -> Any:
    if SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {
            str(item_key): _redact(item, str(item_key))
            for item_key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        redacted = value
        for pattern in SECRET_TEXT:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        return redacted
    return value


def _clip(value: Any, limit: int = 1_500) -> Any:
    redacted = _redact(value)
    serialized = (
        json.dumps(redacted, ensure_ascii=False)
        if isinstance(redacted, (dict, list))
        else redacted
    )
    if not isinstance(serialized, str) or len(serialized) <= limit:
        return redacted
    return {
        "excerpt": serialized[:limit],
        "truncated_characters": len(serialized) - limit,
    }


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _private_write(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def _handoff(snapshot: dict[str, Any], native_status: str) -> str:
    session = snapshot["session"][0]
    messages = snapshot["messages"][-50:]
    message_ids = {message["id"] for message in messages}
    parts = [part for part in snapshot["parts"] if part["message_id"] in message_ids]
    payload = {
        "todos": _clip(snapshot["todos"], 8_000),
        "recent_messages": [_clip(message) for message in messages],
        "recent_parts": [_clip(part) for part in parts],
    }
    return (
        f"# OpenCode handoff: {session['id']}\n\n"
        f"- Native export: {native_status}\n"
        f"- Title: {_clip(session['title'])}\n"
        f"- Directory: {session['directory']}\n"
        f"- Agent: {session.get('agent')}\n"
        f"- Model: {session.get('model')}\n"
        f"- Updated: {session['time_updated']}\n"
        f"- Messages: {len(snapshot['messages'])}\n"
        f"- Parts: {len(snapshot['parts'])}\n\n"
        "The native export status above is independent from the database snapshot.\n\n"
        "## Sanitised cursor evidence\n\n"
        "```json\n"
        f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n"
        "```\n"
    )


def _output_root(session_id: str, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    state_home = os.environ.get("XDG_STATE_HOME")
    if not state_home:
        raise ValueError("XDG_STATE_HOME is required")
    return Path(state_home).resolve() / "agent-session-handoffs" / session_id


def _export(session_id: str, destination: Path) -> int:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"handoff destination already exists: {destination}")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o700)
    stage = Path(tempfile.mkdtemp(prefix=f".{session_id}.", dir=destination.parent))
    os.chmod(stage, 0o700)
    try:
        native = _completed("opencode", "export", session_id)
        stdout = native.stdout.encode()
        stderr = native.stderr.encode()
        native_document: dict[str, Any] | None = None
        try:
            parsed = json.loads(native.stdout)
            if not isinstance(parsed, dict):
                raise TypeError("native export is not a JSON object")
            native_document = parsed
        except (json.JSONDecodeError, TypeError):
            native_status = "invalid"
            native_name = "native-export.invalid.private.log"
        else:
            native_status = "valid" if native.returncode == 0 else "failed"
            native_name = "native-export.private.json"
        if native.returncode != 0:
            native_status = "failed"

        _private_write(stage / native_name, stdout)
        if stderr:
            _private_write(stage / "native-export.stderr.private.log", stderr)

        snapshot = _snapshot(session_id)
        snapshot_bytes = (
            json.dumps(snapshot, indent=2, ensure_ascii=False).encode() + b"\n"
        )
        handoff_bytes = _handoff(snapshot, native_status).encode()
        _private_write(stage / "database-snapshot.private.json", snapshot_bytes)
        _private_write(stage / "handoff.sanitised.md", handoff_bytes)
        manifest = {
            "schema_version": 1,
            "session_id": session_id,
            "native_export": {
                "command": ["opencode", "export", session_id],
                "status": native_status,
                "exit_code": native.returncode,
                "stdout_file": native_name,
                "stdout_sha256": _digest(stdout),
                "stderr_file": (
                    "native-export.stderr.private.log" if stderr else None
                ),
                "stderr_sha256": _digest(stderr) if stderr else None,
                "validated_document": native_document is not None,
            },
            "database_snapshot": {
                "command": ["opencode", "db"],
                "file": "database-snapshot.private.json",
                "sha256": _digest(snapshot_bytes),
                "messages": len(snapshot["messages"]),
                "parts": len(snapshot["parts"]),
                "todos": len(snapshot["todos"]),
            },
            "sanitised_handoff": {
                "file": "handoff.sanitised.md",
                "sha256": _digest(handoff_bytes),
            },
        }
        _private_write(
            stage / "manifest.json",
            json.dumps(manifest, indent=2, ensure_ascii=False).encode() + b"\n",
        )
        stage.replace(destination)
    except BaseException:
        shutil.rmtree(stage)
        raise

    print(
        json.dumps(
            {
                "destination": str(destination),
                "native_status": native_status,
                "messages": len(snapshot["messages"]),
                "parts": len(snapshot["parts"]),
            }
        )
    )
    return 0 if native_status == "valid" else 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("session_id")
    parser.add_argument("--output-dir", type=Path)
    arguments = parser.parse_args()
    if not SESSION_ID.fullmatch(arguments.session_id):
        parser.error("session_id must match ses_<alphanumeric>")
    raise SystemExit(
        _export(
            arguments.session_id,
            _output_root(arguments.session_id, arguments.output_dir),
        )
    )


if __name__ == "__main__":
    main()
