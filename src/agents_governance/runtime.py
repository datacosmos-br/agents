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
from .cleanup import clean_generated
from .command_evals import audit_command_evals
from .commands import CommandSpec, audit_command_specs
from .environment import required_environment
from .native_evals import evaluate_native
from .projection import Projector
from .projection_config import ProjectionConfig, load_projection_config
from .rules import RuleSpec, audit_rule_specs
from .security import ScannerRoute
from .security import audit as audit_security_evidence
from .security import inventory as security_inventory
from .temp import require_repository_storage
from .validation import validate
from .waza import load_eval_suite, require_model_projection, run_preflight

_MODEL = "aihub-primary"


@dataclass(frozen=True)
class RuntimeInventory:
    catalog: Catalog
    projection: ProjectionConfig
    model: str
    commands: tuple[CommandSpec, ...]
    agents: tuple[AgentProfile, ...]
    rules: tuple[RuleSpec, ...]
    security_routes: tuple[ScannerRoute, ...]


def repository_root() -> Path:
    """Return the physical source root that owns this installed runtime."""
    return Path(__file__).resolve().parents[2]


def _catalog(root: Path) -> Catalog:
    catalog = Catalog(root)
    catalog.require_inventory_lock()
    return catalog


def _doctor(root: Path) -> RuntimeInventory:
    catalog = _catalog(root)
    projection = load_projection_config(root)
    require_repository_storage(root)

    model = require_model_projection(root)
    if model != _MODEL:
        raise ValueError(f"Waza model must equal {_MODEL}; got {model}")

    commands = audit_command_specs(
        root, (directory.name for directory in catalog.skill_dirs())
    )
    audit_command_evals(root, commands)

    agents = audit_agent_profiles(root)
    rules = audit_rule_specs(root)

    security_routes = security_inventory((root,))
    audit_security_evidence((root,))
    return RuntimeInventory(
        catalog, projection, model, commands, agents, rules, security_routes
    )


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
    inventory = _doctor(root)
    print(
        "doctor: "
        f"{len(inventory.catalog.skill_dirs())} skills, "
        f"{len(inventory.commands)} commands, {len(inventory.agents)} agents, "
        f"{len(inventory.rules)} rules"
    )


def check(root: Path) -> None:
    inventory = _doctor(root)
    validate(
        inventory.catalog,
        inventory.model,
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
    inventory = _doctor(root)
    projector = Projector(
        inventory.catalog,
        inventory.projection,
        inventory.commands,
        inventory.agents,
        inventory.rules,
    )
    projector.apply()
    print(f"sync: project projection converged at {projector.project_root()}")


def _waza_executable() -> str:
    executable = shutil.which("waza")
    if executable is None:
        raise FileNotFoundError("required executable is unavailable: waza")
    return executable


def evaluate(root: Path) -> None:
    inventory = _doctor(root)
    executable = _waza_executable()
    native = evaluate_native(
        root,
        inventory.projection,
        inventory.commands,
        inventory.agents,
        inventory.rules,
    )
    eval_directories = tuple(
        path.parent for path in sorted((root / "evals").glob("*/eval.yaml"))
    )
    suites = tuple(load_eval_suite(directory) for directory in eval_directories)
    commands: list[tuple[str, ...]] = [
        (executable, "tokens", "check", str(root / "skills"), "--strict")
    ]
    for suite in suites:
        if suite.skill is None:
            raise ValueError(f"skill evaluation has no skill: {suite.path}")
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
        f"evaluate: {len(suites)} skill suites, {native.commands} command, "
        f"{native.agents} agent, and {native.rules} rule artifacts passed"
    )


def secure(root: Path) -> None:
    inventory = _doctor(root)
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
        cwd=root,
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
        cwd=root,
        check=True,
    )
    for route in inventory.security_routes:
        subprocess.run(route.command, cwd=route.root, check=True)
    print(f"secure: {len(inventory.security_routes)} dependency route(s) passed")


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
    inventory = _doctor(root)
    environment = dict(os.environ)
    del environment["CLIPROXY_API_KEY"]
    environment["COPILOT_PROVIDER_API_KEY"] = api_key
    environment["COPILOT_MODEL"] = inventory.model
    run_preflight(root, inventory.model, runner=_live_runner(environment))
    print("live: aihub-primary preflight passed")


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
