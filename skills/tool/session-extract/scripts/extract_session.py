#!/usr/bin/env python3
"""Interpret authenticated private session input; perform no filesystem I/O."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys

Reference = dict[str, str | int]


def _reference(source: str, line: int, locator: object, label: str) -> list[Reference]:
    if locator is None:
        return []
    if not isinstance(locator, str):
        raise TypeError(f"{label} must be text")
    return [
        {
            "source": source,
            "line": line,
            "locator": locator,
            "classification": "unreviewed-reference",
        }
    ]


def _claude_record(event: dict[str, object], source: str, line: int) -> list[Reference]:
    if event.get("type") != "assistant":
        return []
    message = event.get("message")
    if not isinstance(message, dict):
        raise TypeError("Claude assistant event requires message")
    content = message.get("content")
    if not isinstance(content, list):
        raise TypeError("Claude assistant content must be a block list")
    references: list[Reference] = []
    for block in content:
        if not isinstance(block, dict):
            raise TypeError("Claude content block must be an object")
        if block.get("type") == "tool_use":
            arguments = block.get("input")
            if not isinstance(arguments, dict):
                raise TypeError("Claude tool input must be an object")
            references.extend(
                _reference(
                    source, line, arguments.get("file_path"), "Claude tool file_path"
                )
            )
    return references


def _poolside_record(
    event: dict[str, object], source: str, line: int
) -> list[Reference]:
    if event.get("type") != "tool_call.parsed":
        return []
    parsed = event.get("tool_call_parsed")
    if not isinstance(parsed, dict):
        raise TypeError("Poolside tool_call.parsed requires tool_call_parsed")
    arguments = parsed.get("args")
    if not isinstance(arguments, dict):
        raise TypeError("Poolside tool arguments must be an object")
    return _reference(source, line, arguments.get("path"), "Poolside tool path")


_ENVELOPE_RECORDS = {"claude": _claude_record, "poolside": _poolside_record}


def _envelope(parser: argparse.ArgumentParser, args: argparse.Namespace) -> object:
    if args.workspace is None:
        parser.error(f"{args.provider} requires --workspace")
    record = _ENVELOPE_RECORDS[args.provider]
    envelope = json.load(sys.stdin)
    if not isinstance(envelope, dict) or envelope.get("schema_version") != 1:
        raise ValueError("private source envelope requires schema_version 1")
    sources = envelope.get("sources")
    if not isinstance(sources, list):
        raise TypeError("private source envelope requires sources")
    workspaces: dict[str, set[str]] = {}
    events: list[Reference] = []
    references: list[Reference] = []
    attachments: list[dict[str, str]] = []
    for source in sources:
        if not isinstance(source, dict):
            raise TypeError("source entry must be an object")
        session = source.get("session_id")
        locator = source.get("locator")
        encoded = source.get("content_base64")
        role = source.get("role")
        if (
            not isinstance(session, str)
            or not session
            or not isinstance(locator, str)
            or not locator
            or not isinstance(role, str)
            or not role
            or not isinstance(encoded, str)
        ):
            raise TypeError(
                "source requires session_id, locator, content_base64 and role"
            )
        if role not in {"metadata", "events", "attachment"}:
            raise ValueError("source role is not declared")
        content = base64.b64decode(encoded, validate=True)
        workspaces.setdefault(session, set())
        if role == "attachment":
            attachments.append({"session_id": session, "source": locator})
            continue
        for line, text in enumerate(content.decode("utf-8").splitlines(), 1):
            if not text.strip():
                continue
            event = json.loads(text)
            if not isinstance(event, dict):
                raise TypeError(f"{args.provider} event must be an object")
            if role == "metadata" and event.get("cwd") is not None:
                cwd = event["cwd"]
                if not isinstance(cwd, str) or not cwd:
                    raise TypeError(f"{args.provider} cwd metadata must be text")
                workspaces[session].add(cwd)
            events.append(
                {
                    "session_id": session,
                    "source": locator,
                    "line": line,
                    "event_json": text,
                }
            )
            for reference in record(event, locator, line):
                reference["session_id"] = session
                references.append(reference)
    if any(len(values) != 1 for values in workspaces.values()):
        raise ValueError(f"{args.provider} workspace metadata is absent or ambiguous")
    selected = sorted(
        session for session, values in workspaces.items() if args.workspace in values
    )
    if args.action == "inventory":
        if args.session_id is not None:
            parser.error("inventory does not accept --session-id")
        return {
            "schema_version": 1,
            "provider": args.provider,
            "sessions": [
                {"session_id": session, "workspace": args.workspace}
                for session in selected
            ],
        }
    if args.session_id not in selected:
        raise LookupError("session does not belong to the selected workspace")
    return {
        "schema_version": 1,
        "provider": args.provider,
        "classification": "private",
        "session": {"session_id": args.session_id, "workspace": args.workspace},
        "events": [event for event in events if event["session_id"] == args.session_id],
        "references": [
            item for item in references if item["session_id"] == args.session_id
        ],
        "attachments": [
            item for item in attachments if item["session_id"] == args.session_id
        ],
    }


def _zcode(parser: argparse.ArgumentParser, args: argparse.Namespace) -> object:
    if args.action != "extract" or args.session_id is None:
        parser.error("zcode accepts only extract with --session-id")
    seen: set[str] = set()
    messages: list[dict[str, object]] = []
    turns: list[dict[str, object]] = []
    final_request: list[object] = []
    for line_number, raw_line in enumerate(sys.stdin, 1):
        if not raw_line.strip():
            continue
        record = json.loads(raw_line)
        if not isinstance(record, dict):
            raise TypeError(f"ZCode record at line {line_number} must be an object")
        if record.get("sessionId") != args.session_id:
            raise ValueError(f"session identity mismatch at line {line_number}")
        if record.get("type") != "model_io":
            raise ValueError(f"unexpected ZCode record type at line {line_number}")
        request = record.get("request")
        response = record.get("response")
        if not isinstance(request, dict) or not isinstance(response, dict):
            raise TypeError(f"request and response required at line {line_number}")
        snapshot = request.get("messages")
        if not isinstance(snapshot, list):
            raise TypeError(f"request messages required at line {line_number}")
        for index, message in enumerate(snapshot):
            if not isinstance(message, dict):
                raise TypeError(f"message must be an object at line {line_number}")
            canonical = json.dumps(message, sort_keys=True, ensure_ascii=False)
            key = f"{index}:{hashlib.sha256(canonical.encode()).hexdigest()}"
            if key not in seen:
                seen.add(key)
                messages.append(
                    {
                        "source_line": line_number,
                        "message_index": index,
                        "event_json": canonical,
                    }
                )
        final_request = snapshot
        error = record.get("error")
        if error is not None and not isinstance(error, dict):
            raise TypeError(f"error must be an object at line {line_number}")
        turns.append(
            {
                "source_line": line_number,
                "started_at": record.get("startedAt"),
                "completed_at": record.get("completedAt"),
                "request_id": record.get("requestId"),
                "turn_id": record.get("turnId"),
                "response": {
                    "text": response.get("text"),
                    "reasoning_text": response.get("reasoningText"),
                    "tool_calls": response.get("toolCalls"),
                    "finish_reason": response.get("finishReason"),
                },
                "error": error,
            }
        )
    if not turns:
        raise ValueError("ZCode rollout has no records")
    return {
        "schema_version": 1,
        "provider": "zcode",
        "classification": "private",
        "session_id": args.session_id,
        "record_count": len(turns),
        "observed_messages": messages,
        "turns": turns,
        "final_request_messages": final_request,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inventory", "extract"))
    parser.add_argument(
        "--provider", required=True, choices=(*_ENVELOPE_RECORDS, "zcode")
    )
    parser.add_argument("--workspace")
    parser.add_argument("--session-id")
    args = parser.parse_args()
    read = _zcode if args.provider == "zcode" else _envelope
    print(json.dumps(read(parser, args), ensure_ascii=False))


if __name__ == "__main__":
    main()
