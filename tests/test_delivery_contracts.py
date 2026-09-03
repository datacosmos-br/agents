from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_VERBS = {
    "help",
    "doctor",
    "check",
    "sync",
    "evaluate",
    "secure",
    "clean",
    "live",
}
REQUIRED_MAKE_TARGETS = {
    "help",
    "setup",
    "fix",
    "gen",
    "docs",
    "audit",
    "check",
    "static",
    "shell",
    "build",
    "test",
    "spec",
    "coverage",
    "providers",
    "projection",
    "ci",
    "security",
    "temp",
    "validate-live",
}


def test_eval_workflow_covers_integration_push_and_pull_requests() -> None:
    workflow = yaml.load(
        (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    events = workflow["on"]
    required_paths = {
        ".agents/**",
        ".github/dependabot.yml",
        ".github/workflows/**",
        ".mise.toml",
        ".waza.yaml",
        "AGENTS.md",
        "CLAUDE.md",
        "README.md",
        "agents/**",
        "bin/**",
        "commands/**",
        "config/**",
        "docs/**",
        "evals/**",
        "Makefile",
        "pyproject.toml",
        "rules/**",
        "skills/**",
        "src/**",
        "tests/**",
        "uv.lock",
    }

    assert events["push"]["branches"] == ["dev"]
    assert set(events["pull_request"]["branches"]) == {"dev", "main"}
    assert required_paths <= set(events["push"]["paths"])
    assert required_paths <= set(events["pull_request"]["paths"])


def test_dependabot_covers_every_dependency_surface_with_seven_day_cooldown() -> None:
    configuration = yaml.safe_load(
        (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    updates = configuration["updates"]
    expected_surfaces = {
        ("uv", "/"),
        ("npm", "/evals/mcp-server-patterns/fixtures"),
        ("npm", "/evals/nextjs-turbopack/fixtures"),
        ("github-actions", "/"),
    }

    assert configuration["version"] == 2
    assert {
        (update["package-ecosystem"], update["directory"]) for update in updates
    } == expected_surfaces
    assert all(update["schedule"] == {"interval": "weekly"} for update in updates)
    assert all(update["cooldown"]["default-days"] >= 7 for update in updates)


def test_eval_workflow_materializes_derived_shell_storage() -> None:
    workflow = yaml.load(
        (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    commands = tuple(
        step.get("run") for step in workflow["jobs"]["eval"]["steps"] if "run" in step
    )

    assert 'install -d -m 700 "$HOME/tmp"' in commands


def test_eval_workflow_is_the_single_native_ci_owner() -> None:
    workflow_root = ROOT / ".github" / "workflows"
    workflow_paths = tuple(sorted(workflow_root.glob("*.yml")))

    assert [path.name for path in workflow_paths] == ["eval.yml"]
    source = workflow_paths[0].read_text(encoding="utf-8")
    workflow = yaml.load(source, Loader=yaml.BaseLoader)
    steps = workflow["jobs"]["eval"]["steps"]
    actions = tuple(step["uses"] for step in steps if "uses" in step)
    checkout = next(
        step for step in steps if step.get("uses", "").startswith("actions/checkout@")
    )
    commands = tuple(step["run"] for step in steps if "run" in step)

    assert actions
    assert all(re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", action) for action in actions)
    assert checkout["with"] == {"fetch-depth": "0"}
    assert sum("make ci" in command.splitlines() for command in commands) == 1
    assert "|| true" not in source
    assert "conflict-marker" not in source


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


def test_make_is_development_support_for_the_optionless_runtime() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    targets = set(re.findall(r"^([a-z][a-z-]*):", makefile, flags=re.MULTILINE))
    invocations = re.findall(
        r"^\s*@\$\(AGENTSCTL\)\s+([^\s]+)\s*$", makefile, re.MULTILINE
    )

    assert REQUIRED_MAKE_TARGETS <= targets
    assert invocations
    assert set(invocations) <= RUNTIME_VERBS
    assert all("--" not in invocation for invocation in invocations)
    assert "agents-security" not in makefile
    assert "config/waza.mk" not in makefile
    assert "?=" not in makefile
    assert not (ROOT / "config" / "waza.mk").exists()


def test_make_isolates_concurrent_pytest_invocations() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "override export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.venv" in makefile
    assert "override export VIRTUAL_ENV := $(CURDIR)/.venv" in makefile
    assert "PYTEST_SCRATCH := $(CURDIR)/.test-tmp" in makefile
    assert "--basetemp $(PYTEST_SCRATCH)/pytest.$$PPID" in makefile
    assert ".test-tmp/pytest\n" not in makefile


def test_external_token_workflows_are_not_offline_landing_gates() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    ci_prerequisites = re.search(r"^ci:\s*([^#\n]*)", makefile, flags=re.MULTILINE)
    assert ci_prerequisites is not None
    assert "security" not in ci_prerequisites.group(1).split()
    assert "validate-live" not in ci_prerequisites.group(1).split()

    contracts = (
        ROOT / "rules" / "architecture" / "engineering-core.md",
        ROOT
        / "skills"
        / "agent-wide"
        / "verification"
        / "verification-loop"
        / "references"
        / "procedure.md",
        ROOT / "docs" / "execution" / "master-v7" / "06-validation-and-landing.md",
    )
    for path in contracts:
        text = path.read_text(encoding="utf-8").lower()
        assert "external token" in text
        assert "not executed" in text

    validation_contract = contracts[-1].read_text(encoding="utf-8")
    assert "keeps landing open" not in validation_contract
