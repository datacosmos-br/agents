from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents_governance.agent_profiles import AgentProvider
from agents_governance.projection_config import (
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
                surfaces[surface.value] = cell
            contexts[context.value] = surfaces
        providers[provider.value] = contexts
    return {
        "version": 7,
        "manifest_versions": {"projection": 5},
        "providers": providers,
    }


def _write(root: Path, payload: object) -> None:
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "projections.json").write_text(json.dumps(payload), encoding="utf-8")


def test_projection_config_requires_complete_closed_v7_matrix(tmp_path: Path) -> None:
    _write(tmp_path, _matrix())

    config = load_projection_config(tmp_path)

    assert config.version == 7
    assert config.projection_manifest_version == 5
    assert len(config.cells) == 7 * 2 * 4
    assert (
        config.cell("claude", "personal", "skills").status is ProjectionStatus.SUPPORTED
    )
    assert config.cell("claude", "personal", "skills").path == "${HOME}/.claude/skills"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda value: value.update(version=6), "projection config must use version 7"),
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

    assert len(config.cells) == 56
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
