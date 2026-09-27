"""Extract private ZCode model I/O from authenticated JSONL on stdin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def _records() -> Iterator[tuple[int, dict[str, object]]]:
    for line_number, raw_line in enumerate(sys.stdin, 1):
        if not raw_line.strip():
            raise ValueError(f"empty ZCode record at line {line_number}")
        record = json.loads(raw_line)
        if not isinstance(record, dict):
            raise TypeError(f"ZCode record at line {line_number} must be an object")
        yield line_number, record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("extract",))
    parser.add_argument("--session-id", required=True)
    args = parser.parse_args()
    seen: set[str] = set()
    messages: list[dict[str, object]] = []
    turns: list[dict[str, object]] = []
    final_request: list[object] = []
    total = 0
    for line_number, record in _records():
        session_id = record.get("sessionId")
        if session_id != args.session_id:
            raise ValueError(f"session identity mismatch at line {line_number}")
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
            digest = hashlib.sha256(canonical.encode()).hexdigest()
            key = f"{index}:{digest}"
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
        total += 1
    if not total:
        raise ValueError("ZCode rollout has no records")
    result = {
        "schema_version": 1,
        "provider": "zcode",
        "classification": "private",
        "session_id": args.session_id,
        "record_count": total,
        "observed_messages": messages,
        "turns": turns,
        "final_request_messages": final_request,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
