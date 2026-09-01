"""Export one OpenCode session into a private, evidence-preserving handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Never

from agents_governance.cleanup import run_with_cleanup

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
    "message": frozenset({"id", "session_id", "time_created", "time_updated", "data"}),
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


def _data_root() -> Path:
    output = _run("opencode", "debug", "paths")
    for line in output.splitlines():
        label, separator, value = line.partition(" ")
        if separator and label == "data":
            return Path(value.strip()).resolve(strict=True)
    raise ValueError("OpenCode did not report its data path")


def _database(data_root: Path) -> sqlite3.Connection:
    path = (data_root / "opencode.db").resolve(strict=True)
    database = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    database.row_factory = sqlite3.Row
    database.execute("PRAGMA query_only = ON")
    for table, required in TABLE_COLUMNS.items():
        actual = {
            str(row[1]) for row in database.execute(f"PRAGMA table_info({table})")
        }
        missing = required - actual
        if missing:
            database.close()
            raise ValueError(
                f"OpenCode {table} schema is missing: {', '.join(sorted(missing))}"
            )
    return database


def _decode_data(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    decoded: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        raw = item.get("data")
        if not isinstance(raw, str):
            raise TypeError("OpenCode data column is not JSON text")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TypeError("OpenCode data column is not a JSON object")
        decoded.append({**item, "data": data})
    return decoded


def _snapshot(session_id: str, data_root: Path) -> dict[str, Any]:
    with _database(data_root) as database:
        session = [
            dict(row)
            for row in database.execute(
                "SELECT id, project_id, parent_id, directory, title, version, agent, model, "
                "time_created, time_updated FROM session WHERE id=?",
                (session_id,),
            )
        ]
        if len(session) != 1:
            raise LookupError(f"expected exactly one OpenCode session for {session_id}")
        return {
            "schema_version": 1,
            "session": session,
            "todos": [
                dict(row)
                for row in database.execute(
                    "SELECT position, status, priority, content, time_created, time_updated "
                    "FROM todo WHERE session_id=? ORDER BY position",
                    (session_id,),
                )
            ],
            "messages": _decode_data(
                list(
                    database.execute(
                        "SELECT id, time_created, time_updated, data FROM message "
                        "WHERE session_id=? ORDER BY time_created, id",
                        (session_id,),
                    )
                )
            ),
            "parts": _decode_data(
                list(
                    database.execute(
                        "SELECT id, message_id, time_created, time_updated, data FROM part "
                        "WHERE session_id=? ORDER BY time_created, id",
                        (session_id,),
                    )
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


def _raise(error: BaseException) -> Never:
    raise error


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
        return Path(os.path.abspath(explicit))
    return _data_root() / "exports" / session_id


def _validate_destination(destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"handoff destination already exists: {destination}")
    parent = destination.parent
    if not parent.is_dir() or parent.is_symlink() or parent.resolve() != parent:
        raise ValueError(f"handoff destination parent must be physical: {parent}")
    for component in (parent, *parent.parents):
        if component.is_symlink():
            raise ValueError(f"handoff destination traverses symlink: {component}")


def _export(session_id: str, destination: Path) -> int:
    _validate_destination(destination)
    stage = Path(tempfile.mkdtemp(prefix=f".{session_id}.", dir=destination.parent))
    os.chmod(stage, 0o700)
    try:
        stdout_path = stage / "native-export.private.json"
        stderr_path = stage / "native-export.stderr.private.log"
        stdout_descriptor = os.open(
            stdout_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        stderr_descriptor = os.open(
            stderr_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        with (
            os.fdopen(stdout_descriptor, "wb") as stdout_stream,
            os.fdopen(stderr_descriptor, "wb") as stderr_stream,
        ):
            native = subprocess.run(
                ("opencode", "export", session_id),
                check=False,
                stdout=stdout_stream,
                stderr=stderr_stream,
            )
        stdout = stdout_path.read_bytes()
        stderr = stderr_path.read_bytes()
        native_document: dict[str, Any] | None = None
        try:
            parsed = json.loads(stdout)
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

        if native_name != stdout_path.name:
            stdout_path.rename(stage / native_name)
        if not stderr:
            stderr_path.unlink()

        native_manifest = {
            "command": ["opencode", "export", session_id],
            "status": native_status,
            "exit_code": native.returncode,
            "stdout_file": native_name,
            "stdout_sha256": _digest(stdout),
            "stderr_file": ("native-export.stderr.private.log" if stderr else None),
            "stderr_sha256": _digest(stderr) if stderr else None,
            "validated_document": native_document is not None,
        }
        if native.returncode != 0:
            _private_write(
                stage / "manifest.json",
                json.dumps(
                    {
                        "schema_version": 1,
                        "session_id": session_id,
                        "native_export": native_manifest,
                        "database_snapshot": None,
                        "sanitised_handoff": None,
                    },
                    indent=2,
                    ensure_ascii=False,
                ).encode()
                + b"\n",
            )
            stage.replace(destination)
            print(
                json.dumps(
                    {
                        "destination": str(destination),
                        "native_status": native_status,
                    }
                )
            )
            return native.returncode

        snapshot = _snapshot(session_id, _data_root())
        snapshot_bytes = (
            json.dumps(snapshot, indent=2, ensure_ascii=False).encode() + b"\n"
        )
        handoff_bytes = _handoff(snapshot, native_status).encode()
        _private_write(stage / "database-snapshot.private.json", snapshot_bytes)
        _private_write(stage / "handoff.sanitised.md", handoff_bytes)
        manifest = {
            "schema_version": 1,
            "session_id": session_id,
            "native_export": native_manifest,
            "database_snapshot": {
                "source": "opencode.db?mode=ro",
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
    except BaseException as primary:
        run_with_cleanup(lambda: _raise(primary), lambda: shutil.rmtree(stage))

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
