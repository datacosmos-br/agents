from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import cast

import pytest

from agents_governance.agent_profiles import AgentProvider
from agents_governance.projection_config import (
    HookClient,
    HookCoverage,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    load_projection_config,
)

# Why: Sequence/Mapping recursion keeps nested JSON documents assignable under
# invariance (ag-2wq detection-rule fixtures).
type JsonValue = (
    None | bool | int | float | str | Sequence["JsonValue"] | Mapping[str, "JsonValue"]
)
type JsonDocument = dict[str, JsonValue]


def _providers(payload: JsonDocument) -> dict[str, JsonDocument]:
    return cast("dict[str, JsonDocument]", payload["providers"])


def _cell(
    payload: JsonDocument, provider: str, context: str, surface: str
) -> JsonDocument:
    contexts = _providers(payload)[provider]
    surfaces = cast("JsonDocument", contexts[context])
    return cast("JsonDocument", surfaces[surface])


def _supported(path: str, *, max_tokens: int | None = None) -> dict[str, JsonValue]:
    cell: dict[str, JsonValue] = {"status": "SUPPORTED", "path": path}
    if max_tokens is not None:
        cell["max_tokens"] = max_tokens
    return cell


def _unsupported(reason: str = "UNSUPPORTED: no native contract") -> dict[str, str]:
    return {"status": "UNSUPPORTED", "reason": reason}


def _matrix(
    *, project_detection_rules: list[JsonDocument] | None = None
) -> JsonDocument:
    providers: dict[str, JsonValue] = {}
    for provider in AgentProvider:
        contexts: dict[str, JsonValue] = {}
        for context in ProjectionContext:
            prefix = "${HOME}/." if context is ProjectionContext.PERSONAL else "."
            surfaces: dict[str, JsonValue] = {}
            for surface in ProjectionSurface:
                cell = _supported(f"{prefix}{provider.value}/{surface.value}")
                if surface is ProjectionSurface.RULES:
                    cell["layout"] = "directory"
                if surface is ProjectionSurface.HOOKS:
                    cell["events"] = {
                        logical: {
                            "status": "SUPPORTED",
                            "native": [native],
                            "coverage": "exact",
                            "clients": ["local"],
                        }
                        for logical, native in {
                            "context_refresh": "ContextRefresh",
                            "prompt_submit": "PromptSubmit",
                            "session_start": "SessionStart",
                            "subagent_start": "SubagentStart",
                        }.items()
                    }
                surfaces[surface.value] = cell
            contexts[context.value] = surfaces
        providers[provider.value] = contexts
    payload: JsonDocument = {
        "version": 7,
        "manifest_versions": {"hooks": 3, "projection": 6},
        "providers": providers,
    }
    if project_detection_rules is not None:
        payload["project_detection_rules"] = project_detection_rules
    return payload


def _write(root: Path, payload: object) -> None:
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "projections.json").write_text(json.dumps(payload), encoding="utf-8")


def test_projection_config_requires_complete_closed_v7_matrix(tmp_path: Path) -> None:
    _write(tmp_path, _matrix())

    config = load_projection_config(tmp_path)

    assert config.version == 7
    assert config.projection_manifest_version == 6
    assert config.hook_manifest_version == 3
    assert len(config.cells) == 8 * 2 * 5
    assert (
        config.cell("claude", "personal", "skills").status is ProjectionStatus.SUPPORTED
    )
    assert config.cell("claude", "personal", "skills").path == "${HOME}/.claude/skills"


def test_projection_config_owns_optional_project_detection_rules(
    tmp_path: Path,
) -> None:
    rule: JsonDocument = {
        "activate_tags": ["flext"],
        "id": "flext-managed",
        "when": {
            "any": [
                {
                    "paths": ["pyproject.toml"],
                    "pattern": "@flext-managed",
                    "type": "file_contains",
                }
            ]
        },
    }
    _write(tmp_path, _matrix(project_detection_rules=[rule]))

    config = load_projection_config(tmp_path)

    assert tuple(item.rule_id for item in config.project_detection_rules) == (
        "flext-managed",
    )


def test_projection_config_rejects_non_rule_detection_contract(
    tmp_path: Path,
) -> None:
    payload = _matrix()
    payload["project_detection_rules"] = ["flext-managed"]
    _write(tmp_path, payload)

    with pytest.raises(TypeError, match="project detection rules"):
        load_projection_config(tmp_path)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda value: value.update(version=6), "projection config must use version 7"),
        (
            lambda value: _providers(value).pop("codex"),
            "projection providers fields must equal",
        ),
        (
            lambda value: _providers(value)["claude"].pop("project"),
            "projection contexts for claude fields must equal",
        ),
        (
            lambda value: cast(
                "JsonDocument", _providers(value)["claude"]["project"]
            ).pop("agents"),
            "projection surfaces for claude/project fields must equal",
        ),
    ],
)
def test_projection_config_rejects_incomplete_or_legacy_contract(
    tmp_path: Path, mutation: Callable[[JsonDocument], object], message: str
) -> None:
    payload = _matrix()
    mutation(payload)
    _write(tmp_path, payload)

    with pytest.raises((TypeError, ValueError), match=message):
        load_projection_config(tmp_path)


@pytest.mark.parametrize(
    ("cell", "message"),
    [
        ({"status": "SUPPORTED"}, "SUPPORTED cell fields"),
        (
            {"status": "UNSUPPORTED", "reason": "not supported"},
            "UNSUPPORTED reason must start",
        ),
        (
            {"status": "UNSUPPORTED", "reason": "UNSUPPORTED: explicit", "path": "x"},
            "UNSUPPORTED cell fields",
        ),
    ],
)
def test_projection_config_rejects_ambiguous_cells(
    tmp_path: Path, cell: JsonDocument, message: str
) -> None:
    payload = _matrix()
    personal = cast("JsonDocument", _providers(payload)["claude"]["personal"])
    personal["skills"] = cell
    _write(tmp_path, payload)
    with pytest.raises((TypeError, ValueError), match=message):
        load_projection_config(tmp_path)


def test_repository_projection_matrix_classifies_every_cell(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]

    config = load_projection_config(repository)

    assert len(config.cells) == 80
    assert [rule.rule_id for rule in config.project_detection_rules] == [
        "flext-managed"
    ]
    assert config.cell("pool", "project", "skills").status is ProjectionStatus.SUPPORTED
    assert config.cell("pool", "project", "skills").path == ".poolside/skills"
    assert (
        config.cell("pool", "personal", "skills").status is ProjectionStatus.UNSUPPORTED
    )
    assert (
        config.cell("pool", "project", "hooks").status is ProjectionStatus.UNSUPPORTED
    )
    assert (
        config.cell("copilot", "personal", "agents").status
        is ProjectionStatus.SUPPORTED
    )
    assert config.cell("copilot", "project", "agents").path == ".github/agents"
    assert (
        config.cell("gemini", "project", "agents").status is ProjectionStatus.SUPPORTED
    )
    assert (
        config.cell("antigravity", "project", "agents").status
        is ProjectionStatus.UNSUPPORTED
    )
    assert config.cell("codex", "project", "rules").status is ProjectionStatus.SUPPORTED
    assert config.cell("codex", "project", "rules").path == "AGENTS.md"
    assert config.cell("codex", "personal", "skills").path == "${HOME}/.codex/skills"
    codex = config.cell("codex", "project", "hooks").events
    assert codex is not None
    assert codex["context_refresh"].native == ("SessionStart",)
    assert codex["subagent_start"].coverage is HookCoverage.EXACT
    cursor = config.cell("cursor", "project", "hooks").events
    assert cursor is not None
    assert cursor["session_start"].coverage is HookCoverage.EXACT
    assert cursor["session_start"].clients == (HookClient.LOCAL,)
    gemini = config.cell("gemini", "project", "hooks").events
    opencode = config.cell("opencode", "project", "hooks").events
    assert gemini is not None
    assert opencode is not None
    assert gemini["subagent_start"].status is ProjectionStatus.UNSUPPORTED
    assert opencode["subagent_start"].status is ProjectionStatus.UNSUPPORTED


def test_hook_cell_requires_complete_native_event_mapping(tmp_path: Path) -> None:
    payload = _matrix()
    events = cast(
        "JsonDocument", _cell(payload, "claude", "project", "hooks")["events"]
    )
    del events["context_refresh"]
    _write(tmp_path, payload)

    with pytest.raises(ValueError, match="events fields must equal"):
        load_projection_config(tmp_path)


def test_hook_event_requires_native_events_or_unsupported_reason(
    tmp_path: Path,
) -> None:
    payload = _matrix()
    events = cast(
        "JsonDocument", _cell(payload, "claude", "project", "hooks")["events"]
    )
    event = cast("JsonDocument", events["context_refresh"])
    event["native"] = []
    _write(tmp_path, payload)

    with pytest.raises(TypeError, match="native must be a non-empty array"):
        load_projection_config(tmp_path)

    event.clear()
    event.update(
        status="UNSUPPORTED",
        reason="UNSUPPORTED: provider exposes no subagent lifecycle boundary",
    )
    _write(tmp_path, payload)
    config = load_projection_config(tmp_path)
    native_events = config.cell("claude", "project", "hooks").events
    assert native_events is not None
    assert native_events["context_refresh"].status is ProjectionStatus.UNSUPPORTED
