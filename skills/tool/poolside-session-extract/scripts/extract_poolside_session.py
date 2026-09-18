#!/usr/bin/env python3
"""Interpret authenticated private poolside input; perform no filesystem I/O."""

from __future__ import annotations

import argparse
import base64
import json
import sys


def _poolside_record(
    event: dict[str, object], source: str, line: int
) -> list[dict[str, str | int]]:
    if event.get("type") != "tool_call.parsed":
        return []
    parsed = event.get("tool_call_parsed")
    if not isinstance(parsed, dict):
        raise TypeError("Poolside tool_call.parsed requires tool_call_parsed")
    arguments = parsed.get("args")
    if not isinstance(arguments, dict):
        raise TypeError("Poolside tool arguments must be an object")
    locator = arguments.get("path")
    if locator is None:
        return []
    if not isinstance(locator, str):
        raise TypeError("Poolside tool path must be text")
    return [
        {
            "source": source,
            "line": line,
            "locator": locator,
            "classification": "unreviewed-reference",
        }
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inventory", "extract"))
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--session-id")
    args = parser.parse_args()
    envelope = json.load(sys.stdin)
    if not isinstance(envelope, dict) or envelope.get("schema_version") != 1:
        raise ValueError("private source envelope requires schema_version 1")
    sources = envelope.get("sources")
    if not isinstance(sources, list):
        raise TypeError("private source envelope requires sources")
    workspaces: dict[str, set[str]] = {}
    events: list[dict[str, str | int]] = []
    references: list[dict[str, str | int]] = []
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
                raise TypeError("poolside event must be an object")
            if role == "metadata" and event.get("cwd") is not None:
                cwd = event["cwd"]
                if not isinstance(cwd, str) or not cwd:
                    raise TypeError("poolside cwd metadata must be text")
                workspaces[session].add(cwd)
            events.append(
                {
                    "session_id": session,
                    "source": locator,
                    "line": line,
                    "event_json": text,
                }
            )
            for reference in _poolside_record(event, locator, line):
                reference["session_id"] = session
                references.append(reference)
    if any(len(values) != 1 for values in workspaces.values()):
        raise ValueError("poolside workspace metadata is absent or ambiguous")
    selected = sorted(
        session for session, values in workspaces.items() if args.workspace in values
    )
    sessions = [
        {"session_id": session, "workspace": args.workspace} for session in selected
    ]
    if args.action == "inventory":
        if args.session_id is not None:
            parser.error("inventory does not accept --session-id")
        result = {"schema_version": 1, "provider": "poolside", "sessions": sessions}
    else:
        if args.session_id not in selected:
            raise LookupError("session does not belong to the selected workspace")
        result = {
            "schema_version": 1,
            "provider": "poolside",
            "classification": "private",
            "session": {"session_id": args.session_id, "workspace": args.workspace},
            "events": [
                event for event in events if event["session_id"] == args.session_id
            ],
            "references": [
                item for item in references if item["session_id"] == args.session_id
            ],
            "attachments": [
                item for item in attachments if item["session_id"] == args.session_id
            ],
        }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
