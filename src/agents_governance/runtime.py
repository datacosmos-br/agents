"""Complete optionless workflows behind the public ``agentsctl`` verbs."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .agent_profiles import AgentProfile, audit_agent_profiles
from .catalog import Catalog
from .cleanup import clean_generated, run_atomic_publications
from .command_evals import audit_command_evals
from .commands import CommandSpec, audit_command_specs
from .environment import required_environment
from .governance_config import (
    GovernanceConfig,
    audit_governance_config,
    load_governance_config,
)
from .hook_projection import HookProjector
from .native_evals import evaluate_native
from .projection import Projector
from .projection_authorization import load_project_authorization
from .projection_config import load_projection_config
from .rules import RuleSpec, audit_rule_specs
from .security import ScannerRoute
from .security import audit as audit_security_evidence
from .security import inventory as security_inventory
from .temp import require_repository_storage
from .validation import validate
from .waza import (
    EvalSuiteSpec,
    load_eval_suite,
    require_model_projection,
    run_live_corpus,
)

_MODEL = "aihub-primary"


@dataclass(frozen=True)
class RuntimeInventory:
    catalog: Catalog
    governance: GovernanceConfig
    commands: tuple[CommandSpec, ...]
    agents: tuple[AgentProfile, ...]
    rules: tuple[RuleSpec, ...]


def repository_root() -> Path:
    """Return the physical source root that owns this installed runtime."""
    return Path(__file__).resolve().parents[2]


def _catalog(root: Path) -> Catalog:
    catalog = Catalog(root)
    catalog.require_inventory_lock()
    return catalog


def _inventory(root: Path) -> RuntimeInventory:
    """Load only the native governance inventory shared by its consumers."""

    catalog = _catalog(root)
    require_repository_storage(root)
    commands = audit_command_specs(
        root, (directory.name for directory in catalog.skill_dirs())
    )
    audit_command_evals(root, commands)

    agents = audit_agent_profiles(root)
    rules = audit_rule_specs(root)
    governance = load_governance_config(root)
    audit_governance_config(root, governance, catalog, commands, rules)
    return RuntimeInventory(catalog, governance, commands, agents, rules)


def _model(root: Path) -> str:
    model = require_model_projection(root)
    if model != _MODEL:
        raise ValueError(f"Waza model must equal {_MODEL}; got {model}")
    return model


def _security(root: Path) -> tuple[ScannerRoute, ...]:
    routes = security_inventory((root,))
    audit_security_evidence((root,))
    return routes


def help_workflow(_root: Path) -> None:
    print(
        "agentsctl\n"
        "  help\n"
        "  doctor\n"
        "  check\n"
        "  sync\n"
        "  evaluate\n"
        "  secure\n"
        "  clean\n"
        "  live"
    )


def doctor(root: Path) -> None:
    inventory = _inventory(root)
    print(
        "doctor: "
        f"{len(inventory.catalog.skill_dirs())} skills, "
        f"{len(inventory.commands)} commands, {len(inventory.agents)} agents, "
        f"{len(inventory.rules)} rules"
    )


def check(root: Path) -> None:
    inventory = _inventory(root)
    load_projection_config(root)
    model = _model(root)
    validate(
        inventory.catalog,
        model,
        inventory.commands,
        inventory.agents,
        inventory.rules,
    )
    print(
        "check: "
        f"{len(inventory.catalog.skill_dirs())} skills, "
        f"{len(inventory.commands)} commands, {len(inventory.agents)} agents, "
        f"{len(inventory.rules)} rules"
    )


def sync(root: Path) -> None:
    inventory = _inventory(root)
    projection = load_projection_config(root)
    projector = Projector(
        inventory.catalog,
        projection,
        inventory.commands,
        inventory.agents,
        inventory.rules,
    )
    project = projector.project_root()
    authorization = load_project_authorization(project)
    hooks = HookProjector(
        inventory.governance,
        projection,
        inventory.commands,
        inventory.rules,
    )
    run_atomic_publications(
        (
            *projector.publications(authorization),
            *hooks.publications(authorization),
        )
    )
    if authorization.selected:
        print(f"sync: personal and project projections converged at {project}")
    else:
        print(
            f"sync: personal projections converged; project not selected at {project}"
        )


def _waza_executable() -> str:
    executable = shutil.which("waza")
    if executable is None:
        raise FileNotFoundError("required executable is unavailable: waza")
    return executable


def _skill_suites(root: Path) -> tuple[EvalSuiteSpec, ...]:
    eval_directories = tuple(
        path.parent for path in sorted((root / "evals").glob("*/eval.yaml"))
    )
    return tuple(load_eval_suite(directory) for directory in eval_directories)


def evaluate(root: Path) -> None:
    inventory = _inventory(root)
    projection = load_projection_config(root)
    _model(root)
    executable = _waza_executable()
    native = evaluate_native(
        root,
        projection,
        inventory.commands,
        inventory.agents,
        inventory.rules,
    )
    suites = _skill_suites(root)
    commands: list[tuple[str, ...]] = [
        (executable, "tokens", "check", str(root / "skills"), "--strict")
    ]
    for suite in suites:
        skill = inventory.catalog.record(suite.skill).directory
        commands.append(
            (
                executable,
                "spec",
                "verify",
                "--skill",
                str(skill),
                "--eval",
                str(suite.path),
                "--fail",
            )
        )
    for command in commands:
        subprocess.run(command, cwd=root, check=True)
    print(
        f"evaluate: {len(suites)} skill specifications and {native.commands} command, "
        f"{native.agents} agent, and {native.rules} rule artifacts verified offline"
    )


def secure(_root: Path) -> None:
    target = Projector.project_root()
    require_repository_storage(target)
    routes = _security(target)
    token = required_environment("SNYK_TOKEN")
    environment = dict(os.environ)
    environment["SNYK_TOKEN"] = token
    executables = {name: shutil.which(name) for name in ("gitleaks", "semgrep", "snyk")}
    missing = tuple(name for name, path in executables.items() if path is None)
    if missing:
        raise FileNotFoundError(
            "required security executable is unavailable: " + ", ".join(missing)
        )
    subprocess.run(
        (
            str(executables["gitleaks"]),
            "dir",
            "--no-banner",
            "--exit-code",
            "1",
            "--redact",
            ".",
        ),
        cwd=target,
        env=environment,
        check=True,
    )
    subprocess.run(
        (
            str(executables["semgrep"]),
            "scan",
            "--jobs",
            "1",
            "--config",
            "p/default",
            "--error",
            "--metrics=off",
            "--no-git-ignore",
            "--exclude",
            ".git",
            "--exclude",
            ".venv",
            "--exclude",
            ".cache",
            "--exclude",
            ".test-tmp",
            "--exclude",
            "results",
            ".",
        ),
        cwd=target,
        env=environment,
        check=True,
    )
    for route in routes:
        subprocess.run(route.command, cwd=route.root, env=environment, check=True)
    print(f"secure: {len(routes)} dependency route(s) passed")


def clean(root: Path) -> None:
    removed = clean_generated(root)
    print(f"clean: removed {len(removed)} generated path(s)")


def _live_runner(
    environment: dict[str, str],
) -> Callable[[Sequence[str], Path], None]:
    def run(command: Sequence[str], root: Path) -> None:
        subprocess.run(command, cwd=root, env=environment, check=True)

    return run


def live(root: Path) -> None:
    api_key = required_environment(
        "CLIPROXY_API_KEY", conflicts=("COPILOT_PROVIDER_API_KEY",)
    )
    model = _model(root)
    executable = _waza_executable()
    environment = dict(os.environ)
    del environment["CLIPROXY_API_KEY"]
    environment["COPILOT_PROVIDER_API_KEY"] = api_key
    environment["COPILOT_MODEL"] = model
    suites = _skill_suites(root)
    run_live_corpus(
        root,
        model,
        suites,
        executable,
        runner=_live_runner(environment),
    )
    task_count = 1 + sum(len(suite.tasks) for suite in suites)
    print(f"live: aihub-primary passed {len(suites) + 1} suites and {task_count} tasks")


WORKFLOWS = {
    "help": help_workflow,
    "doctor": doctor,
    "check": check,
    "sync": sync,
    "evaluate": evaluate,
    "secure": secure,
    "clean": clean,
    "live": live,
}


__all__ = ("WORKFLOWS", "repository_root")
