from __future__ import annotations

import json
from pathlib import Path

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


def _supported(path: str, *, max_tokens: int | None = None) -> dict[str, object]:
    cell: dict[str, object] = {"status": "SUPPORTED", "path": path}
    if max_tokens is not None:
        cell["max_tokens"] = max_tokens
    return cell


def _unsupported(reason: str = "UNSUPPORTED: no native contract") -> dict[str, str]:
    return {"status": "UNSUPPORTED", "reason": reason}


def _matrix() -> dict[str, object]:
    providers: dict[str, object] = {}
    for provider in AgentProvider:
        contexts: dict[str, object] = {}
        for context in ProjectionContext:
            prefix = "${HOME}/." if context is ProjectionContext.PERSONAL else "."
            surfaces: dict[str, object] = {}
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
    return {
        "version": 6,
        "manifest_versions": {"hooks": 3, "projection": 5},
        "providers": providers,
    }


def _write(root: Path, payload: object) -> None:
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "projections.json").write_text(json.dumps(payload), encoding="utf-8")


def test_projection_config_requires_complete_closed_v6_matrix(tmp_path: Path) -> None:
    _write(tmp_path, _matrix())

    config = load_projection_config(tmp_path)

    assert config.version == 6
    assert config.projection_manifest_version == 5
    assert config.hook_manifest_version == 3
    assert len(config.cells) == 7 * 2 * 5
    assert (
        config.cell("claude", "personal", "skills").status is ProjectionStatus.SUPPORTED
    )
    assert config.cell("claude", "personal", "skills").path == "${HOME}/.claude/skills"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda value: value.update(version=5), "projection config must use version 6"),
        (
            lambda value: value["providers"].pop("codex"),
            "projection providers must equal",
        ),
        (
            lambda value: value["providers"]["claude"].pop("project"),
            "projection contexts for claude must equal",
        ),
        (
            lambda value: value["providers"]["claude"]["project"].pop("agents"),
            "projection surfaces for claude/project must equal",
        ),
    ],
)
def test_projection_config_rejects_incomplete_or_legacy_contract(
    tmp_path: Path, mutation: object, message: str
) -> None:
    payload = _matrix()
    mutation(payload)  # type: ignore[operator]
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
    tmp_path: Path, cell: dict[str, object], message: str
) -> None:
    payload = _matrix()
    payload["providers"]["claude"]["personal"]["skills"] = cell  # type: ignore[index]
    _write(tmp_path, payload)

    with pytest.raises((TypeError, ValueError), match=message):
        load_projection_config(tmp_path)


def test_repository_projection_matrix_classifies_every_cell(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]

    config = load_projection_config(repository)

    assert len(config.cells) == 70
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
    del payload["providers"]["claude"]["project"]["hooks"]["events"][  # type: ignore[index]
        "context_refresh"
    ]
    _write(tmp_path, payload)

    with pytest.raises(ValueError, match="events must equal"):
        load_projection_config(tmp_path)


def test_hook_event_requires_native_events_or_unsupported_reason(
    tmp_path: Path,
) -> None:
    payload = _matrix()
    event = payload["providers"]["claude"]["project"]["hooks"]["events"][  # type: ignore[index]
        "context_refresh"
    ]
    event["native"] = []  # type: ignore[index]
    _write(tmp_path, payload)

    with pytest.raises(TypeError, match="native must be a non-empty array"):
        load_projection_config(tmp_path)

    event.clear()  # type: ignore[union-attr]
    event.update(  # type: ignore[union-attr]
        status="UNSUPPORTED",
        reason="UNSUPPORTED: provider exposes no subagent lifecycle boundary",
    )
    _write(tmp_path, payload)
    config = load_projection_config(tmp_path)
    events = config.cell("claude", "project", "hooks").events
    assert events is not None
    assert events["context_refresh"].status is ProjectionStatus.UNSUPPORTED
