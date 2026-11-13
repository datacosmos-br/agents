"""Exercise provider-specific parsers through authenticated public skill resources."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest

from agents_governance import GovernanceBundle


def _source(provider: str, workspace: str, session: str) -> list[dict[str, str]]:
    metadata = (
        json.dumps({"type": "queue-operation"}) + "\n" + json.dumps({"cwd": workspace})
    )
    if provider == "claude":
        event = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "complete evidence " * 2000},
                    {
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": "docs/plans/design.md"},
                    },
                ]
            },
        }
    else:
        event = {
            "type": "tool_call.parsed",
            "tool_call_parsed": {
                "name": "write_file",
                "args": {
                    "path": "docs/plans/design.md",
                    "content": "complete evidence " * 2000,
                },
            },
        }
    return [
        {
            "session_id": session,
            "role": role,
            "locator": locator,
            "content_base64": base64.b64encode(content).decode("ascii"),
        }
        for role, locator, content in (
            ("metadata", "metadata.jsonl", metadata.encode()),
            ("events", "events.jsonl", json.dumps(event).encode()),
            ("attachment", "research.bin", bytes(range(256))),
        )
    ]


def _command(
    bundle: GovernanceBundle, provider: str, workspace: str
) -> tuple[str, ...]:
    return (
        sys.executable,
        _script(bundle),
        "--provider",
        provider,
        "--workspace",
        workspace,
    )


def _script(bundle: GovernanceBundle) -> str:
    skill = next(item for item in bundle.skills if item.name == "session-extract")
    scripts = tuple((skill.directory / "scripts").glob("*.py"))
    assert len(scripts) == 1
    return str(scripts[0])


@pytest.mark.parametrize("provider", ("claude", "poolside"))
def test_complete_private_evidence_and_references_without_effects(
    governance_bundle: GovernanceBundle, tmp_path: Path, provider: str
) -> None:
    workspace = str(tmp_path / "selected")
    sources = _source(provider, workspace, "selected-session")
    sources.extend(_source(provider, str(tmp_path / "other"), "unrelated-session"))
    request = json.dumps({"schema_version": 1, "sources": sources}).encode()
    command = _command(governance_bundle, provider, workspace)
    inventory = subprocess.run(
        (*command, "inventory"),
        input=request,
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    assert json.loads(inventory.stdout)["sessions"] == [
        {"session_id": "selected-session", "workspace": workspace}
    ]
    invocation = (*command, "extract", "--session-id", "selected-session")
    extracted = subprocess.run(
        invocation, input=request, cwd=tmp_path, capture_output=True, check=True
    )
    repeated = subprocess.run(
        invocation, input=request, cwd=tmp_path, capture_output=True, check=True
    )
    assert extracted.stdout == repeated.stdout
    assert not extracted.stderr
    payload = json.loads(extracted.stdout)
    assert payload["classification"] == "private"
    expected = base64.b64decode(sources[1]["content_base64"]).decode()
    assert expected in [event["event_json"] for event in payload["events"]]
    assert payload["references"][0]["locator"] == "docs/plans/design.md"
    assert payload["attachments"][0]["source"] == "research.bin"
    assert b"unrelated-session" not in extracted.stdout
    assert not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("provider", ("claude", "poolside"))
def test_malformed_record_fails_without_private_stdout_or_effects(
    governance_bundle: GovernanceBundle, tmp_path: Path, provider: str
) -> None:
    workspace = str(tmp_path / "selected")
    sources = _source(provider, workspace, "selected-session")
    sources[1]["content_base64"] = base64.b64encode(
        b"malformed-private-record"
    ).decode()
    command = _command(governance_bundle, provider, workspace)
    result = subprocess.run(
        (*command, "extract", "--session-id", "selected-session"),
        input=json.dumps({"schema_version": 1, "sources": sources}).encode(),
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert not result.stdout
    assert b"JSONDecodeError" in result.stderr
    assert b"malformed-private-record" not in result.stderr
    assert not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("provider", ("claude", "poolside"))
def test_empty_inventory_is_distinct_from_unknown_extraction(
    governance_bundle: GovernanceBundle, tmp_path: Path, provider: str
) -> None:
    command = _command(governance_bundle, provider, str(tmp_path / "selected"))
    request = json.dumps({"schema_version": 1, "sources": []}).encode()
    inventory = subprocess.run(
        (*command, "inventory"), input=request, capture_output=True, check=True
    )
    assert json.loads(inventory.stdout)["sessions"] == []
    unknown = subprocess.run(
        (*command, "extract", "--session-id", "missing"),
        input=request,
        capture_output=True,
        check=False,
    )
    assert unknown.returncode != 0
    assert not unknown.stdout


@pytest.mark.parametrize("provider", ("claude", "poolside"))
def test_ambiguous_metadata_is_not_guessed(
    governance_bundle: GovernanceBundle, tmp_path: Path, provider: str
) -> None:
    workspace = str(tmp_path / "selected")
    sources = _source(provider, workspace, "selected-session")
    original = base64.b64decode(sources[0]["content_base64"])
    sources[0]["content_base64"] = base64.b64encode(
        original + b'\n{"cwd":"/other"}'
    ).decode()
    result = subprocess.run(
        (*_command(governance_bundle, provider, workspace), "inventory"),
        input=json.dumps({"schema_version": 1, "sources": sources}).encode(),
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert not result.stdout
    assert b"absent or ambiguous" in result.stderr


def _zcode_record(session: str, text: str) -> str:
    return json.dumps(
        {
            "sessionId": session,
            "type": "model_io",
            "request": {"messages": [{"role": "user", "content": text}]},
            "response": {"text": "answer", "finishReason": "stop"},
        }
    )


def test_zcode_rollout_yields_private_turns_and_rejects_another_session(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    command = (sys.executable, _script(governance_bundle), "--provider", "zcode")
    rollout = "\n".join(_zcode_record("selected", text) for text in ("one", "one"))
    extracted = subprocess.run(
        (*command, "extract", "--session-id", "selected"),
        input=rollout.encode(),
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    payload = json.loads(extracted.stdout)
    assert payload["classification"] == "private"
    assert payload["record_count"] == 2
    assert len(payload["observed_messages"]) == 1
    mismatched = subprocess.run(
        (*command, "extract", "--session-id", "other"),
        input=rollout.encode(),
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    assert mismatched.returncode != 0
    assert not mismatched.stdout
    assert b"session identity mismatch" in mismatched.stderr
    assert not tuple(tmp_path.iterdir())
