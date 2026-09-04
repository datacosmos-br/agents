from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _active_contracts() -> tuple[Path, ...]:
    fixed = (
        ROOT / "AGENTS.md",
        ROOT / "README.md",
    )
    trees = (
        ROOT / "commands",
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
        ROOT / "workflows",
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
        body = " ".join(path.read_text(encoding="utf-8").lower().split())
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

    # `.codex/hooks.json` and `.claude/settings.json` are declared project
    # projection destinations, so their presence on disk is runtime state, not
    # a defect. What must never happen is a suspended tracker command reaching
    # an agent through them, so assert on content when the file exists.
    for path in (ROOT / ".codex" / "hooks.json", ROOT / ".claude" / "settings.json"):
        if not path.exists():
            continue
        assert command.search(path.read_text(encoding="utf-8")) is None, (
            path.relative_to(ROOT)
        )


def test_source_repository_does_not_select_or_contain_project_projection() -> None:
    """No derived projection artifact may be versioned or offered as source.

    The invariant is about *what Git carries*, not about what a directory
    entry happens to exist on one developer's disk. This repository is a
    registered Gas City rig, so the pack runtime legitimately writes skill
    symlinks and an ownership manifest into `.claude/skills` and
    `.codex/skills` at any moment, without asking. Asserting that those
    directories do not exist made a green suite depend on whether an
    unrelated daemon had run recently: a clean checkout goes red minutes
    later with no commit in between.

    So the assertion is what Git can see. A projection artifact is a defect
    when it is tracked, staged, or offered as untracked source; a runtime
    projection that `.gitignore` already excludes is correct operation.
    """

    projection = re.compile(
        r"^(?:\.(?:agents|claude|codex|cursor|gemini|opencode)/"
        r"|\.github/(?:agents|hooks|instructions|skills)/"
        r"|GEMINI\.md$)"
    )
    commitable_selection = ".agents/projection.json"

    tracked = subprocess.run(
        ("git", "ls-files", "-z"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")
    offered = subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=all", "-z"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")

    assert [
        path
        for path in tracked
        if path and projection.match(path) and path != commitable_selection
    ] == []
    assert [
        entry[3:]
        for entry in offered
        if entry[3:]
        and projection.match(entry[3:])
        and entry[3:] != commitable_selection
    ] == []

    assert (
        subprocess.run(
            ("git", "check-ignore", "-q", commitable_selection),
            cwd=ROOT,
            check=False,
        ).returncode
        == 1
    )
    assert (
        subprocess.run(
            ("git", "check-ignore", "-q", ".claude/settings.json"),
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )
    assert (
        subprocess.run(
            ("git", "ls-files", "--", "AGENTS.md"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == "AGENTS.md"
    )

    # A generated capsule must never be merged into the canonical instruction.
    assert "AIHUB-GOVERNANCE-INSTRUCTIONS" not in (ROOT / "AGENTS.md").read_text(
        encoding="utf-8"
    )


def test_every_project_projection_destination_is_ignored() -> None:
    """Each project-scope destination must be excluded from source control.

    The previous guard checked artifacts one hand-maintained path list at a
    time, so a newly supported provider silently escaped it. Here the list of
    destinations is derived from `config/projections.json` itself: add a
    project-scope destination without ignoring it and this fails, naming the
    surface that would be offered as source.
    """

    payload = json.loads(
        (ROOT / "config" / "projections.json").read_text(encoding="utf-8")
    )

    destinations: set[str] = set()
    for provider in payload["providers"].values():
        for surface in provider.get("project", {}).values():
            if surface.get("status") != "SUPPORTED":
                continue
            destination = surface["path"]
            # Root-level canonical files (AGENTS.md, CLAUDE.md) are source that
            # the projector rewrites in place, not a projection-only artifact.
            if "/" not in destination:
                continue
            destinations.add(destination)

    assert destinations, "no project-scope destination resolved"

    unignored = sorted(
        destination
        for destination in destinations
        if subprocess.run(
            ("git", "check-ignore", "-q", destination),
            cwd=ROOT,
            check=False,
        ).returncode
        != 0
    )
    assert unignored == [], unignored


def test_additive_orchestration_contract_separates_selection_from_installation() -> (
    None
):
    gascity = (ROOT / "rules" / "coordination" / "gascity.md").read_text(
        encoding="utf-8"
    )
    beads = (ROOT / "rules" / "workflow" / "beads-traceability.md").read_text(
        encoding="utf-8"
    )

    assert "Installation never selects" in gascity
    assert "without Beads" in gascity
    assert "selects Beads" in beads
    assert all(term in beads for term in ("Git", "PR", "review", "checks", "CI"))
