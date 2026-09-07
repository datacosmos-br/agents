#!/usr/bin/env python3
"""Extract Claude Code session history to sanitised handoff markdown.

Reads the JSONL transcript and reconstructs a full conversation flow with
tool calls, results, thinking blocks, and user messages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SECRET_KEY = re.compile(
    r"(?:authorization|cookie|credential|password|secret|token|api[_-]?key)",
    re.IGNORECASE,
)
SECRET_TEXT = (
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)((?:set-)?cookie\s*[:=]\s*)[^\r\n]+"),
    re.compile(
        r"""(?i)(["']?(?:api[_-]?key|authorization|credential|token|password|secret)"""
        r"""["']?\s*[:=]\s*["']?)[^"',}\r\n]+"""
    ),
)


def _redact(value: Any, key: str = "") -> Any:
    if SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        redacted = value
        for pattern in SECRET_TEXT:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        return redacted
    return value


def _clip(value: Any, limit: int = 1500) -> Any:
    redacted = _redact(value)
    serialized = (
        json.dumps(redacted, ensure_ascii=False)
        if isinstance(redacted, (dict, list))
        else str(redacted)
    )
    if len(serialized) <= limit:
        return redacted
    return {"excerpt": serialized[:limit], "truncated_characters": len(serialized) - limit}


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _find_project_hash(session_id: str, claude_dir: Path) -> str | None:
    projects_dir = claude_dir / "projects"
    if not projects_dir.exists():
        return None
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        session_file = project_dir / f"{session_id}.jsonl"
        if session_file.exists():
            return project_dir.name
    return None


def _load_session(session_file: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with open(session_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARN: invalid JSON at line {line_num}: {e}", file=sys.stderr)
    return entries


def _load_history(session_id: str, claude_dir: Path) -> dict[str, Any] | None:
    history_file = claude_dir / "history.jsonl"
    if not history_file.exists():
        return None
    with open(history_file) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("sessionId") == session_id:
                    return entry
            except json.JSONDecodeError:
                continue
    return None


def _extract_text(content: Any) -> str:
    """Extract text from Claude message content (string or array)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))
                elif item.get("type") == "thinking":
                    thinking = item.get("thinking", "")
                    if thinking.strip():
                        parts.append(f"[thinking: {thinking[:200]}]")
        return " ".join(parts)
    return str(content)


def _extract_conversation(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract ordered conversation from Claude JSONL entries."""
    conversation: list[dict[str, Any]] = []
    pending_tool_calls: dict[str, dict[str, Any]] = {}

    for entry in entries:
        entry_type = entry.get("type", "")

        if entry_type == "user":
            msg = entry.get("message", {})
            content = msg.get("content", "")

            # Check if this is a tool_result wrapper
            if isinstance(content, list):
                has_tool_results = any(
                    isinstance(c, dict) and c.get("type") == "tool_result"
                    for c in content
                )
                if has_tool_results:
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "tool_result":
                            tc_id = item.get("tool_use_id", "")
                            result_content = item.get("content", "")
                            if tc_id in pending_tool_calls:
                                pending_tool_calls[tc_id]["result"] = {
                                    "content": _clip(_extract_text(result_content), 1000),
                                }
                                conversation.append(pending_tool_calls.pop(tc_id))
                            else:
                                conversation.append({
                                    "role": "tool_result",
                                    "tool_id": tc_id,
                                    "result": {
                                        "content": _clip(_extract_text(result_content), 1000),
                                    },
                                    "timestamp": entry.get("timestamp"),
                                })
                    continue

            text = _clip(_extract_text(content), 2000)
            if text:
                conversation.append({
                    "role": "user",
                    "content": text,
                    "timestamp": entry.get("timestamp"),
                })

        elif entry_type == "assistant":
            msg = entry.get("message", {})
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue

            for item in content:
                if not isinstance(item, dict):
                    continue

                if item.get("type") == "tool_use":
                    tc_id = item.get("id", "")
                    tool_name = item.get("name", "unknown")
                    tool_input = item.get("input", {})
                    pending_tool_calls[tc_id] = {
                        "role": "tool_call",
                        "tool_name": tool_name,
                        "tool_id": tc_id,
                        "input": _clip(tool_input, 800),
                        "timestamp": entry.get("timestamp"),
                        "result": None,
                    }
                    conversation.append(pending_tool_calls[tc_id])

                elif item.get("type") == "thinking":
                    thinking = item.get("thinking", "")
                    if thinking.strip():
                        conversation.append({
                            "role": "reasoning",
                            "content": _clip(thinking, 1500),
                            "timestamp": entry.get("timestamp"),
                        })

                elif item.get("type") == "text":
                    text = item.get("text", "")
                    if text.strip():
                        conversation.append({
                            "role": "assistant",
                            "content": _clip(text, 2000),
                            "timestamp": entry.get("timestamp"),
                        })

    return conversation


def _generate_handoff(
    session_id: str,
    history: dict[str, Any] | None,
    conversation: list[dict[str, Any]],
    project_hash: str,
) -> str:
    lines = [
        f"# Claude Session Handoff: {session_id}",
        "",
    ]

    if history:
        lines.extend([
            f"- Display: {history.get('display', 'N/A')}",
            f"- Project: {history.get('project', 'N/A')}",
            f"- Timestamp: {history.get('timestamp', 'N/A')}",
        ])

    lines.extend([
        f"- Project hash: {project_hash}",
        f"- Conversation turns: {len(conversation)}",
        "",
    ])

    # Conversation flow
    if conversation:
        lines.extend(["## Conversation Flow", ""])
        for turn in conversation:
            role = turn.get("role", "unknown")
            ts = turn.get("timestamp", "")

            if role == "user":
                lines.append(f"### User [{ts}]")
                lines.append(turn.get("content", ""))
                lines.append("")

            elif role == "tool_call":
                tool_name = turn.get("tool_name", "unknown")
                tool_input = turn.get("input", {})
                result = turn.get("result")
                lines.append(f"### Tool Call: `{tool_name}` [{ts}]")
                if isinstance(tool_input, dict):
                    if "command" in tool_input:
                        cmd = tool_input["command"]
                        desc = tool_input.get("description", "")
                        if desc:
                            lines.append(f"_{desc}_")
                        lines.append(f"```bash\n{cmd}\n```")
                    elif "skill" in tool_input:
                        lines.append(f"Skill: `{tool_input['skill']}`")
                    else:
                        lines.append(f"```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```")
                if result:
                    content = result.get("content", "")
                    lines.append(f"Result: {content}")
                lines.append("")

            elif role == "tool_result":
                result = turn.get("result", {})
                lines.append(f"### Tool Result [{ts}]")
                lines.append(result.get("content", ""))
                lines.append("")

            elif role == "reasoning":
                lines.append(f"### Reasoning [{ts}]")
                lines.append(f"> {turn.get('content', '')}")
                lines.append("")

            elif role == "assistant":
                lines.append(f"### Assistant [{ts}]")
                lines.append(turn.get("content", ""))
                lines.append("")

    lines.extend([
        "## Resume Command",
        "",
        "```bash",
        f"claude --resume {session_id}",
        "```",
    ])

    return "\n".join(str(line) for line in lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Claude session to handoff")
    parser.add_argument("session_id", help="Claude session UUID")
    parser.add_argument(
        "--claude-dir",
        type=Path,
        default=Path.home() / ".claude",
        help="Claude data directory (default: ~/.claude)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: ~/.local/state/claude/exports/<session-id>)",
    )
    args = parser.parse_args()

    session_id = args.session_id
    claude_dir = args.claude_dir.resolve()

    if not claude_dir.exists():
        print(f"ERROR: Claude directory not found: {claude_dir}", file=sys.stderr)
        raise SystemExit(1)

    project_hash = _find_project_hash(session_id, claude_dir)
    if not project_hash:
        print(f"ERROR: Session {session_id} not found in any project", file=sys.stderr)
        raise SystemExit(1)

    session_file = claude_dir / "projects" / project_hash / f"{session_id}.jsonl"
    if not session_file.exists():
        print(f"ERROR: Session file not found: {session_file}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Found session {session_id} in project {project_hash}")

    entries = _load_session(session_file)
    print(f"Loaded {len(entries)} entries")

    history = _load_history(session_id, claude_dir)
    conversation = _extract_conversation(entries)
    handoff = _generate_handoff(session_id, history, conversation, project_hash)

    output_dir = args.output_dir or (Path.home() / ".local/state/claude/exports" / session_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    handoff_file = output_dir / "handoff.sanitised.md"
    handoff_file.write_text(handoff)

    # Write structured conversation for programmatic use
    conv_file = output_dir / "conversation.private.json"
    conv_file.write_text(json.dumps(conversation, indent=2, ensure_ascii=False) + "\n")
    os.chmod(conv_file, 0o600)

    manifest = {
        "schema_version": 2,
        "session_id": session_id,
        "project_hash": project_hash,
        "source_file": str(session_file),
        "source_sha256": _digest(session_file.read_bytes()),
        "entries": len(entries),
        "conversation_turns": len(conversation),
        "handoff_file": str(handoff_file),
        "handoff_sha256": _digest(handoff.encode()),
    }
    manifest_file = output_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(f"Handoff: {handoff_file}")
    print(f"Manifest: {manifest_file}")
    print(json.dumps({
        "destination": str(output_dir),
        "entries": len(entries),
        "conversation_turns": len(conversation),
    }))


if __name__ == "__main__":
    main()
