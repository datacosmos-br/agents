#!/usr/bin/env python3
"""Extract Poolside trajectory NDJSON to sanitised handoff markdown.

Reads both the ACP/TUI logs and the trajectory NDJSON to reconstruct
a full conversation flow with tool calls, results, and reasoning.
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
    return {
        "excerpt": serialized[:limit],
        "truncated_characters": len(serialized) - limit,
    }


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _find_session_dir(session_id: str, logs_root: Path) -> Path | None:
    if not logs_root.exists():
        return None
    for workspace_dir in logs_root.iterdir():
        if not workspace_dir.is_dir():
            continue
        session_dir = workspace_dir / session_id
        if session_dir.exists() and (session_dir / "acp.log.jsonl").exists():
            return session_dir
    return None


def _find_trajectory(session_id: str, trajectories_root: Path) -> Path | None:
    if not trajectories_root.exists():
        return None
    candidate = trajectories_root / f"trajectory-standalone_{session_id}.ndjson"
    return candidate if candidate.exists() else None


def _load_ndjson(file_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not file_path.exists():
        return entries
    with open(file_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARN: invalid JSON at line {line_num}: {e}", file=sys.stderr)
    return entries


def _extract_acp_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    event_counts: dict[str, int] = {}
    tool_calls = []
    errors = []
    session_config: dict[str, Any] = {}

    for entry in entries:
        msg = entry.get("msg", "unknown")
        event_counts[msg] = event_counts.get(msg, 0) + 1

        if "session_id" in entry:
            session_config["session_id"] = entry["session_id"]
        if "thought_level" in entry:
            session_config["thought_level"] = entry["thought_level"]
        if "requested_agent_name" in entry:
            session_config["agent"] = entry["requested_agent_name"]
        if "cwd" in entry:
            session_config["cwd"] = entry["cwd"]

        if msg == "model sampled multiple tool calls":
            tool_calls.append(
                {
                    "step_id": entry.get("step_id", ""),
                    "tools": entry.get("tools", []),
                    "count": entry.get("tool_calls_count", 0),
                }
            )

        if entry.get("level") == "ERROR":
            errors.append(
                {
                    "time": entry.get("time", ""),
                    "msg": msg,
                    "error": entry.get("err", entry.get("error", "")),
                }
            )

    return {
        "event_counts": event_counts,
        "session_config": session_config,
        "tool_calls": tool_calls,
        "errors": errors,
    }


def _extract_tui_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    event_counts: dict[str, int] = {}
    user_messages = []
    file_ops = []

    for entry in entries:
        msg = entry.get("msg", "unknown")
        event_counts[msg] = event_counts.get(msg, 0) + 1

        if msg == "Queued user message":
            user_messages.append({"time": entry.get("time", "")})
        if msg == "Wrote text file":
            file_ops.append(
                {
                    "path": entry.get("path", ""),
                    "bytes": entry.get("bytes", 0),
                }
            )

    return {
        "event_counts": event_counts,
        "user_messages": user_messages,
        "file_ops": file_ops,
    }


def _extract_trajectory_conversation(
    trajectory_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extract ordered conversation from trajectory NDJSON.

    Returns a list of conversation turns: user prompts, tool calls with
    results, and assistant reasoning.
    """
    conversation: list[dict[str, Any]] = []
    pending_tool_calls: dict[str, dict[str, Any]] = {}

    for entry in trajectory_entries:
        entry_type = entry.get("type", "")

        if entry_type == "session.start":
            meta = entry.get("session_start", {})
            conversation.append(
                {
                    "role": "system",
                    "content": f"Session started with agent: {meta.get('agent_name', 'unknown')}",
                    "timestamp": entry.get("timestamp"),
                }
            )

        elif entry_type == "session.input":
            inp = entry.get("session_input", {})
            prompt = inp.get("prompt", "")
            mode = inp.get("mode", "unknown")
            # Strip system context wrapper
            if "<context>" in prompt:
                prompt_end = prompt.find("</context>")
                if prompt_end > 0:
                    prompt = prompt[prompt_end + 10 :].strip()
            # Strip post_user_message reminders
            if "Updated secrets" in prompt:
                idx = prompt.find("Updated secrets")
                if idx > 0:
                    prompt = prompt[:idx].strip()
            if prompt:
                conversation.append(
                    {
                        "role": "user",
                        "content": _clip(prompt, 2000),
                        "timestamp": entry.get("timestamp"),
                        "mode": mode,
                    }
                )

        elif entry_type == "tool_call.parsed":
            parsed = entry.get("tool_call_parsed", {})
            tc_id = parsed.get("id", "")
            tool_name = parsed.get("name", "unknown")
            args = parsed.get("args", {})
            pending_tool_calls[tc_id] = {
                "role": "tool_call",
                "tool_name": tool_name,
                "tool_id": tc_id,
                "args": _clip(args, 800),
                "timestamp": entry.get("timestamp"),
                "result": None,
            }

        elif entry_type == "tool_call.result":
            result = entry.get("tool_call_result", {})
            tc_id = result.get("id", "")
            observation = result.get("observation", "")
            tool_name = result.get("tool_name", "unknown")
            success = result.get("success", None)
            todo_result = result.get("todo_action_tool_result")

            if tc_id in pending_tool_calls:
                pending_tool_calls[tc_id]["result"] = {
                    "observation": _clip(observation, 1000),
                    "success": success,
                    "tool_name": tool_name,
                    "todo_result": _clip(todo_result, 500) if todo_result else None,
                }
                conversation.append(pending_tool_calls.pop(tc_id))
            else:
                conversation.append(
                    {
                        "role": "tool_result",
                        "tool_name": tool_name,
                        "tool_id": tc_id,
                        "result": {
                            "observation": _clip(observation, 1000),
                            "success": success,
                        },
                        "timestamp": entry.get("timestamp"),
                    }
                )

        elif entry_type == "thought.end":
            thought = entry.get("thought_end", {})
            text = thought.get("thought", "")
            if text:
                conversation.append(
                    {
                        "role": "reasoning",
                        "content": _clip(text, 1500),
                        "timestamp": entry.get("timestamp"),
                    }
                )

    return conversation


def _generate_handoff(
    session_id: str,
    acp_summary: dict[str, Any],
    tui_summary: dict[str, Any],
    conversation: list[dict[str, Any]],
    session_dir: Path,
    trajectory_path: Path | None,
) -> str:
    config = acp_summary.get("session_config", {})

    lines = [
        f"# Poolside Session Handoff: {session_id}",
        "",
        f"- Agent: {config.get('agent', 'N/A')}",
        f"- CWD: {config.get('cwd', 'N/A')}",
        f"- Thought level: {config.get('thought_level', 'N/A')}",
        f"- Session dir: {session_dir}",
    ]
    if trajectory_path:
        lines.append(f"- Trajectory: {trajectory_path}")
    lines.append("")

    # Event summary
    lines.extend(["## ACP Event Summary", "", "```"])
    for event_type, count in sorted(
        acp_summary["event_counts"].items(), key=lambda x: -x[1]
    ):
        lines.append(f"{count:4d} {event_type}")
    lines.extend(["```", ""])

    if tui_summary["event_counts"]:
        lines.extend(["## TUI Event Summary", "", "```"])
        for event_type, count in sorted(
            tui_summary["event_counts"].items(), key=lambda x: -x[1]
        ):
            lines.append(f"{count:4d} {event_type}")
        lines.extend(["```", ""])

    # Conversation flow
    if conversation:
        lines.extend(["## Conversation Flow", ""])
        for turn in conversation:
            role = turn.get("role", "unknown")
            ts = turn.get("timestamp", "")

            if role == "user":
                lines.extend((f"### User [{ts}]", turn.get("content", ""), ""))

            elif role == "tool_call":
                tool_name = turn.get("tool_name", "unknown")
                args = turn.get("args", {})
                result = turn.get("result")
                lines.append(f"### Tool Call: `{tool_name}` [{ts}]")
                if isinstance(args, dict):
                    if "cmd" in args:
                        lines.append(f"```bash\n{args['cmd']}\n```")
                    elif "action" in args:
                        lines.append(f"Action: `{args['action']}`")
                        if "content" in args:
                            lines.append(f"Content: {args['content']}")
                    elif "path" in args:
                        lines.append(f"Path: `{args['path']}`")
                    else:
                        lines.append(
                            f"```json\n{json.dumps(args, indent=2, ensure_ascii=False)}\n```"
                        )
                if result:
                    obs = result.get("observation", "")
                    success = result.get("success")
                    status = (
                        "OK"
                        if success
                        else "FAILED"
                        if success is not None
                        else "unknown"
                    )
                    lines.append(f"Result [{status}]: {obs}")
                lines.append("")

            elif role == "tool_result":
                tool_name = turn.get("tool_name", "unknown")
                result = turn.get("result", {})
                obs = result.get("observation", "")
                success = result.get("success")
                status = (
                    "OK" if success else "FAILED" if success is not None else "unknown"
                )
                lines.extend(
                    (f"### Tool Result: `{tool_name}` [{status}] [{ts}]", obs, "")
                )

            elif role == "reasoning":
                lines.extend(
                    (f"### Reasoning [{ts}]", f"> {turn.get('content', '')}", "")
                )

    # Tool call summary
    if acp_summary["tool_calls"]:
        lines.extend(["## Tool Call Batches", ""])
        for tc in acp_summary["tool_calls"][-20:]:
            lines.append(
                f"- Step {tc['step_id'][:16]}: {', '.join(tc['tools'])} (x{tc['count']})"
            )
        lines.append("")

    # File operations from TUI
    if tui_summary["file_ops"]:
        lines.extend(["## File Operations (TUI)", ""])
        for op in tui_summary["file_ops"]:
            lines.append(f"- {op['path']} ({op['bytes']} bytes)")
        lines.append("")

    # Errors
    if acp_summary["errors"]:
        lines.extend(["## Errors", ""])
        for err in acp_summary["errors"]:
            lines.append(f"- [{err['time']}] {err['msg']}: {_clip(err['error'], 200)}")
        lines.append("")

    # Todo items from conversation
    todo_items = [
        t
        for t in conversation
        if t.get("role") == "tool_call" and t.get("tool_name") == "todo_action"
    ]
    if todo_items:
        lines.extend(["## Todo Items", ""])
        for item in todo_items:
            args = item.get("args", {})
            result = item.get("result", {})
            todo_result = result.get("todo_result") if result else None
            action = args.get("action", "")
            content = args.get("content", "")
            if action == "add" and content:
                lines.append(f"- [added] {content}")
            elif action == "set_in_progress" and content:
                lines.append(f"- [in_progress] {content}")
            elif todo_result:
                lines.append(f"- [{action}] {todo_result}")
        lines.append("")

    lines.extend(
        [
            "## Resume",
            "",
            "To resume this session, use the poolside CLI with the session ID.",
        ]
    )

    return "\n".join(str(line) for line in lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Poolside session to handoff")
    parser.add_argument("session_id", help="Poolside session UUID")
    parser.add_argument(
        "--logs-root",
        type=Path,
        default=Path.home() / ".local/state/poolside/pool/logs",
        help="Poolside logs root",
    )
    parser.add_argument(
        "--trajectories-root",
        type=Path,
        default=Path.home() / ".local/state/poolside/trajectories",
        help="Poolside trajectories root",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: ~/.local/state/poolside/exports/<session-id>)",
    )
    args = parser.parse_args()

    session_id = args.session_id
    logs_root = args.logs_root.resolve()
    trajectories_root = args.trajectories_root.resolve()

    session_dir = _find_session_dir(session_id, logs_root)
    trajectory_path = _find_trajectory(session_id, trajectories_root)

    if not session_dir and not trajectory_path:
        print(
            f"ERROR: Session {session_id} not found in {logs_root} or {trajectories_root}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(f"Session {session_id}")

    acp_entries: list[dict[str, Any]] = []
    tui_entries: list[dict[str, Any]] = []
    trajectory_entries: list[dict[str, Any]] = []

    if session_dir:
        print(f"  ACP/TUI logs: {session_dir}")
        acp_log = session_dir / "acp.log.jsonl"
        tui_log = session_dir / "tui.log.jsonl"
        acp_entries = _load_ndjson(acp_log)
        tui_entries = _load_ndjson(tui_log)
        print(f"  ACP: {len(acp_entries)} entries, TUI: {len(tui_entries)} entries")

    if trajectory_path:
        print(f"  Trajectory: {trajectory_path}")
        trajectory_entries = _load_ndjson(trajectory_path)
        print(f"  Trajectory: {len(trajectory_entries)} entries")

    acp_summary = _extract_acp_summary(acp_entries)
    tui_summary = _extract_tui_summary(tui_entries)
    conversation = _extract_trajectory_conversation(trajectory_entries)

    handoff = _generate_handoff(
        session_id,
        acp_summary,
        tui_summary,
        conversation,
        session_dir or Path(f"(not found: {session_id})"),
        trajectory_path,
    )

    output_dir = args.output_dir or (
        Path.home() / ".local/state/poolside/exports" / session_id
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    handoff_file = output_dir / "handoff.sanitised.md"
    handoff_file.write_text(handoff)

    # Write private raw data
    if acp_entries:
        acp_private = output_dir / "acp-log.private.jsonl"
        acp_private.write_text("\n".join(json.dumps(e) for e in acp_entries) + "\n")
        os.chmod(acp_private, 0o600)

    if tui_entries:
        tui_private = output_dir / "tui-log.private.jsonl"
        tui_private.write_text("\n".join(json.dumps(e) for e in tui_entries) + "\n")
        os.chmod(tui_private, 0o600)

    if trajectory_entries:
        traj_private = output_dir / "trajectory.private.jsonl"
        traj_private.write_text(
            "\n".join(json.dumps(e) for e in trajectory_entries) + "\n"
        )
        os.chmod(traj_private, 0o600)

    # Write conversation as structured JSON for programmatic use
    conv_file = output_dir / "conversation.private.json"
    conv_file.write_text(json.dumps(conversation, indent=2, ensure_ascii=False) + "\n")
    os.chmod(conv_file, 0o600)

    manifest = {
        "schema_version": 2,
        "session_id": session_id,
        "source_dir": str(session_dir) if session_dir else None,
        "trajectory_file": str(trajectory_path) if trajectory_path else None,
        "acp_entries": len(acp_entries),
        "tui_entries": len(tui_entries),
        "trajectory_entries": len(trajectory_entries),
        "conversation_turns": len(conversation),
        "handoff_file": str(handoff_file),
        "handoff_sha256": _digest(handoff.encode()),
        "acp_sha256": _digest((session_dir / "acp.log.jsonl").read_bytes())
        if session_dir
        else None,
        "tui_sha256": _digest((session_dir / "tui.log.jsonl").read_bytes())
        if session_dir
        else None,
        "trajectory_sha256": _digest(trajectory_path.read_bytes())
        if trajectory_path
        else None,
    }
    manifest_file = output_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(f"Handoff: {handoff_file}")
    print(f"Manifest: {manifest_file}")
    print(
        json.dumps(
            {
                "destination": str(output_dir),
                "acp_entries": len(acp_entries),
                "tui_entries": len(tui_entries),
                "trajectory_entries": len(trajectory_entries),
                "conversation_turns": len(conversation),
            }
        )
    )


if __name__ == "__main__":
    main()
