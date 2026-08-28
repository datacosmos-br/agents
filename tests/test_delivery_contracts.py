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
        "skills.lock.json",
        "src/**",
        "tests/**",
        "uv.lock",
    }

    assert events["push"]["branches"] == ["dev"]
    assert set(events["pull_request"]["branches"]) == {"dev", "main"}
    assert required_paths <= set(events["push"]["paths"])
    assert required_paths <= set(events["pull_request"]["paths"])


def test_eval_workflow_materializes_derived_shell_storage() -> None:
    workflow = yaml.load(
        (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    commands = tuple(
        step.get("run") for step in workflow["jobs"]["eval"]["steps"] if "run" in step
    )

    assert 'install -d -m 700 "$HOME/tmp"' in commands


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
