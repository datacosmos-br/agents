"""Complete optionless workflows behind the public ``agentsctl`` verbs."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path

from .agent_profiles import audit_agent_profiles
from .catalog import Catalog
from .cleanup import clean_generated
from .command_evals import audit_command_evals
from .commands import audit_command_specs
from .environment import required_environment
from .normalize import normalize, normalize_descriptions
from .projection import Projector
from .projection_config import load_projection_config
from .rules import audit_rule_specs
from .security import audit as audit_security_evidence
from .security import inventory as security_inventory
from .temp import repository_findings, storage_manifest
from .validation import validate
from .waza import PreflightExit, default_model, load_eval_suite, run_preflight
from .waza import findings as waza_findings

_MODEL = "aihub-primary"


def repository_root() -> Path:
    """Return the physical source root that owns this installed runtime."""
    return Path(__file__).resolve().parents[2]


def _require_empty(items: Iterable[object], context: str) -> None:
    first = next(iter(items), None)
    if first is not None:
        raise ValueError(f"{context}: {first}")


def _catalog(root: Path) -> Catalog:
    catalog = Catalog(root)
    catalog.require_valid()
    _require_empty(catalog.inventory_lock_findings(), "skill inventory lock")
    return catalog


def _doctor(root: Path) -> tuple[Catalog, int, int, int]:
    catalog = _catalog(root)
    load_projection_config(root)
    storage_manifest()

    model = default_model(root)
    if model != _MODEL:
        raise ValueError(f"Waza model must equal {_MODEL}; got {model}")
    _require_empty(waza_findings(root), "Waza configuration")

    commands = audit_command_specs(
        root, (directory.name for directory in catalog.skill_dirs())
    )
    _require_empty(commands.findings, "command source")
    command_evals = audit_command_evals(root, commands.commands)
    _require_empty(command_evals.findings, "command evaluation")

    agents = audit_agent_profiles(root)
    _require_empty(agents.findings, "agent source")
    rules = audit_rule_specs(root)
    _require_empty(rules.findings, "rule source")

    inventory = security_inventory((root,))
    _require_empty(inventory.findings, "security inventory")
    _require_empty(audit_security_evidence((root,)), "security evidence")
    return catalog, len(commands.commands), len(agents.profiles), len(rules.rules)


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
    catalog, commands, agents, rules = _doctor(root)
    print(
        "doctor: "
        f"{len(catalog.skill_dirs())} skills, {commands} commands, "
        f"{agents} agents, {rules} rules"
    )


def check(root: Path) -> None:
    catalog, commands, agents, rules = _doctor(root)
    _require_empty(validate(catalog), "governance validation")
    _require_empty(repository_findings(root), "repository storage")
    _require_empty(normalize(catalog, apply=False), "skill normalization drift")
    _require_empty(
        normalize_descriptions(catalog, apply=False), "skill description drift"
    )
    print(
        "check: "
        f"{len(catalog.skill_dirs())} skills, {commands} commands, "
        f"{agents} agents, {rules} rules"
    )


def sync(root: Path) -> None:
    catalog, _, _, _ = _doctor(root)
    _require_empty(
        Projector(catalog).apply("personal", surface="all"),
        "personal projection",
    )
    print("sync: personal projections converged")


def _waza_executable() -> str:
    executable = shutil.which("waza")
    if executable is None:
        raise FileNotFoundError("required executable is unavailable: waza")
    return executable


def evaluate(root: Path) -> None:
    catalog, _, _, _ = _doctor(root)
    executable = _waza_executable()
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
        skill = catalog.record(suite.skill).directory
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
    print(f"evaluate: {len(suites)} skill suites passed")


def secure(root: Path) -> None:
    result = security_inventory((root,))
    _require_empty(result.findings, "security inventory")
    _require_empty(audit_security_evidence((root,)), "security evidence")
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
            "--exclude",
            "$HOME",
            ".",
        ),
        cwd=root,
        check=True,
    )
    for route in result.routes:
        subprocess.run(route.command, cwd=route.root, check=True)
    print(f"secure: {len(result.routes)} dependency route(s) passed")


def clean(root: Path) -> None:
    removed = clean_generated(root)
    print(f"clean: removed {len(removed)} generated path(s)")


def _live_runner(
    environment: dict[str, str],
) -> Callable[[Sequence[str], Path], int]:
    def run(command: Sequence[str], root: Path) -> int:
        subprocess.run(command, cwd=root, env=environment, check=True)
        return 0

    return run


def live(root: Path) -> None:
    api_key = required_environment(
        "CLIPROXY_API_KEY", conflicts=("COPILOT_PROVIDER_API_KEY",)
    )
    _doctor(root)
    environment = dict(os.environ)
    environment["COPILOT_PROVIDER_API_KEY"] = api_key
    environment["COPILOT_MODEL"] = _MODEL
    result = run_preflight(root, runner=_live_runner(environment))
    if result.status is not PreflightExit.AVAILABLE:
        raise RuntimeError(result.message)
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
