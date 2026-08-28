from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_eval_workflow_covers_integration_push_and_pull_requests() -> None:
    workflow = yaml.load(
        (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    events = workflow["on"]
    required_paths = {
        ".waza.yaml",
        "AGENTS.md",
        "CLAUDE.md",
        "UNIVERSAL_CORE.md",
        "agents/**",
        "commands/**",
        "docs/**",
        "evals/**",
        "skills/**",
        "src/**",
        "tests/**",
        "config/**",
        "Makefile",
    }

    assert events["push"]["branches"] == ["dev"]
    assert set(events["pull_request"]["branches"]) == {"dev", "main"}
    assert required_paths <= set(events["push"]["paths"])
    assert required_paths <= set(events["pull_request"]["paths"])


def test_makefile_exposes_no_cross_repository_mcp_target() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert re.search(r"^mcp\s*:", makefile, flags=re.MULTILINE) is None
    assert "ai-hub mcp" not in makefile


def test_removed_mcp_target_is_not_advertised() -> None:
    paths = (
        ROOT / "workflows" / "WORKFLOWS.md",
        ROOT / "docs" / "execution" / "master-v7" / "repositories" / "agents.md",
    )

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "make mcp" not in text
        assert "MCP drift" not in text
