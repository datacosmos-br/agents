from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _active_contracts() -> tuple[Path, ...]:
    fixed = (
        ROOT / "AGENTS.md",
        ROOT / "README.md",
    )
    trees = (
        ROOT / "docs" / "adr",
        ROOT / "docs" / "execution" / "master-v7",
        ROOT / "rules",
        ROOT / "evals" / "anti-phase-skip",
        ROOT / "evals" / "beads",
        ROOT / "evals" / "beads-worker",
        ROOT / "evals" / "context-canary",
        ROOT / "evals" / "fix-forward-collaboration",
        ROOT / "evals" / "operator-correction-learning",
        ROOT / "evals" / "sprint-closure",
        ROOT / "skills" / "agent-wide" / "anti-phase-skip",
        ROOT / "skills" / "agent-wide" / "context-canary",
        ROOT / "skills" / "agent-wide" / "fix-forward-collaboration",
        ROOT / "skills" / "agent-wide" / "operator-correction-learning",
        ROOT / "skills" / "agent-wide" / "sprint-closure",
        ROOT / "skills" / "tool" / "beads",
        ROOT / "skills" / "tool" / "beads-orchestrator",
        ROOT / "skills" / "tool" / "beads-worker",
        ROOT / "skills" / "tool" / "gascity-change-lifecycle",
        ROOT / "skills" / "tool" / "gascity-workspace-lifecycle",
    )
    discovered = tuple(
        path
        for tree in trees
        for pattern in ("*.md", "*.yaml")
        for path in tree.rglob(pattern)
        if path.is_file() and not path.is_symlink()
    )
    return (*fixed, *discovered)


def test_suspended_tracker_has_no_substitute_ledger() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    historical = (ROOT / "docs" / "execution" / "manual-ledger.md").read_text(
        encoding="utf-8"
    )

    assert "docs/execution/manual-ledger.md" not in agents
    assert historical.startswith("# Historical execution record — sealed\n")
    assert "Do not append to it." in historical

    forbidden = ("manual ledger", "manual-ledger", "execution ledger")
    for path in _active_contracts():
        body = path.read_text(encoding="utf-8").lower()
        assert not any(term in body for term in forbidden), path.relative_to(ROOT)

    required = (
        ROOT / "rules" / "coordination" / "operator-precedence.md",
        ROOT / "rules" / "workflow" / "beads-traceability.md",
        ROOT / "skills" / "tool" / "beads" / "SKILL.md",
    )
    for path in required:
        body = path.read_text(encoding="utf-8").lower()
        assert "create no" in body, path.relative_to(ROOT)
        assert "tracker" in body, path.relative_to(ROOT)
        assert "ledger" in body, path.relative_to(ROOT)


def test_suspended_tracker_tools_have_no_active_command_projection() -> None:
    command = re.compile(r'(?m)^\s*(?:bd|gt|gc)\s|"command"\s*:\s*"(?:bd|gt|gc)\s')

    for path in (ROOT / "AGENTS.md", ROOT / "CLAUDE.md"):
        assert command.search(path.read_text(encoding="utf-8")) is None, (
            path.relative_to(ROOT)
        )

    assert not (ROOT / ".codex" / "hooks.json").exists()
    assert not (ROOT / ".claude" / "settings.json").exists()


def test_source_repository_does_not_select_or_contain_project_projection() -> None:
    assert not (ROOT / ".agents" / "projection.json").exists()
    assert not (ROOT / "GEMINI.md").exists()
    assert "AIHUB-GOVERNANCE-INSTRUCTIONS" not in (ROOT / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    for path in (
        ROOT / ".agents",
        ROOT / ".claude",
        ROOT / ".codex",
        ROOT / ".cursor",
        ROOT / ".gemini",
        ROOT / ".opencode",
        ROOT / ".github" / "agents",
        ROOT / ".github" / "hooks",
        ROOT / ".github" / "instructions",
        ROOT / ".github" / "skills",
    ):
        assert not path.exists(), path.relative_to(ROOT)


def test_additive_orchestration_contract_separates_selection_from_installation() -> (
    None
):
    gascity = (ROOT / "rules" / "gascity.md").read_text(encoding="utf-8")
    beads = (ROOT / "rules" / "workflow" / "beads-traceability.md").read_text(
        encoding="utf-8"
    )

    assert "Installation never selects" in gascity
    assert "without Beads" in gascity
    assert "selects Beads" in beads
    assert all(term in beads for term in ("Git", "PR", "review", "checks", "CI"))
