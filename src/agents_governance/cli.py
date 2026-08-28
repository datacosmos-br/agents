"""Command-line facade for canonical ~/.agents governance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .atomic_io import atomic_write_text
from .catalog import Catalog
from .cleanup import clean_generated
from .command_evals import audit_command_evals
from .commands import (
    CommandArtifact,
    CommandAudit,
    CommandProvider,
    CommandRenderError,
    CommandTokenBudget,
    UnsupportedCommand,
    audit_command_specs,
    render_command,
    waza_bpe_counter,
)
from .normalize import normalize, normalize_descriptions
from .projection import Projector
from .security import audit as security_audit
from .temp import gc as temp_gc
from .temp import gc_all as temp_gc_all
from .temp import global_findings as temp_global_findings
from .temp import repository_findings, run_command
from .temp import status as temp_status
from .validation import validate
from .waza import apply as apply_waza_config
from .waza import default_model as waza_default_model
from .waza import findings as waza_config_findings
from .waza import publish_artifact as publish_waza_artifact
from .waza import run_preflight
from .waza import validate_artifact as validate_waza_artifact
from .waza import validate_model_catalog as validate_waza_model_catalog


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _catalog(root: Path) -> Catalog:
    return Catalog(root)


def _audit(root: Path, write: bool) -> int:
    try:
        catalog = _catalog(root)
        if write:
            atomic_write_text(root / "skills.lock.json", catalog.render_inventory())
        findings = catalog.inventory_lock_findings()
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"FAIL: inventory audit: {error}", file=sys.stderr)
        return 2
    for finding in findings:
        print(f"{finding.path}: {finding.code}: {finding.message}", file=sys.stderr)
    if findings:
        print(
            f"FAIL: {len(findings)} blocking inventory lock finding(s)",
            file=sys.stderr,
        )
        return 1
    count = len(catalog.skill_dirs())
    if write:
        print(f"PASS: wrote skills.lock.json for {count} skill(s)")
    else:
        print(f"PASS: skills.lock.json matches {count} discovered skill(s)")
    return 0


def _validate(root: Path, skill: str | None) -> int:
    catalog = _catalog(root)
    findings = validate(catalog)
    if skill is not None:
        try:
            record = catalog.record(skill)
        except (KeyError, ValueError) as error:
            print(f"FAIL: {error}", file=sys.stderr)
            return 2
        skill_prefix = record.directory.relative_to(root).as_posix() + "/"
        scoped_prefixes = (skill_prefix, f"evals/{skill}/")
        findings = [item for item in findings if item.path.startswith(scoped_prefixes)]
    for item in findings:
        print(f"{item.path}: {item.code}: {item.message}", file=sys.stderr)
    if findings:
        print(f"FAIL: {len(findings)} blocking finding(s)", file=sys.stderr)
        return 1
    print(f"PASS: {len(catalog.skill_dirs())} skills validated")
    return 0


def _command_audit(root: Path) -> CommandAudit:
    catalog = _catalog(root)
    return audit_command_specs(
        root, (directory.name for directory in catalog.skill_dirs())
    )


def _commands_audit(root: Path) -> int:
    try:
        audit = _command_audit(root)
    except (OSError, TypeError, ValueError) as error:
        print(f"FAIL: command audit: {error}", file=sys.stderr)
        return 2
    for command_finding in audit.findings:
        print(
            f"{command_finding.path}: {command_finding.code}: "
            f"{command_finding.message}",
            file=sys.stderr,
        )
    if audit.findings:
        print(
            f"FAIL: {len(audit.findings)} blocking command finding(s)",
            file=sys.stderr,
        )
        return 1
    eval_audit = audit_command_evals(root, audit.commands)
    for eval_finding in eval_audit.findings:
        print(
            f"{eval_finding.path}: {eval_finding.code}: {eval_finding.message}",
            file=sys.stderr,
        )
    if eval_audit.findings:
        print(
            f"FAIL: {len(eval_audit.findings)} blocking command eval finding(s)",
            file=sys.stderr,
        )
        return 1
    print(
        f"PASS: {len(audit.commands)} commands and "
        f"{len(eval_audit.specs)} eval suites validated"
    )
    return 0


def _commands_render(
    root: Path, slug: str, provider: str, max_tokens: int | None
) -> int:
    try:
        audit = _command_audit(root)
    except (OSError, TypeError, ValueError) as error:
        print(f"FAIL: command audit: {error}", file=sys.stderr)
        return 2
    for item in audit.findings:
        print(f"{item.path}: {item.code}: {item.message}", file=sys.stderr)
    if audit.findings:
        print(
            f"FAIL: {len(audit.findings)} blocking command finding(s)",
            file=sys.stderr,
        )
        return 1
    selected = tuple(command for command in audit.commands if command.name == slug)
    if len(selected) != 1:
        print(f"FAIL: unknown canonical command: {slug}", file=sys.stderr)
        return 2
    try:
        rendered = render_command(
            selected[0],
            CommandProvider(provider),
            token_budget=CommandTokenBudget(max_tokens, waza_bpe_counter(root)),
        )
    except (CommandRenderError, OSError, RuntimeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    if isinstance(rendered, UnsupportedCommand):
        print(
            f"{rendered.provider.value}/{rendered.slug}: {rendered.reason}",
            file=sys.stderr,
        )
        return 2
    assert isinstance(rendered, CommandArtifact)
    print(rendered.content, end="")
    return 0


def _project(
    root: Path,
    apply: bool,
    scope: str,
    target: str | None,
    surface: str,
    project_roots: tuple[Path, ...],
) -> int:
    projector = Projector(_catalog(root))
    findings = (
        projector.apply(scope, target, surface, project_roots)
        if apply
        else projector.check(scope, target, surface, project_roots)
    )
    for item in findings:
        print(f"{item.target}: {item.path}: {item.message}", file=sys.stderr)
    if findings:
        return 1
    print("PASS: projections converged")
    return 0


def _discover_projects(root: Path, project_roots: tuple[Path, ...]) -> int:
    projector = Projector(_catalog(root))
    projects, findings = projector.resolve_projects(project_roots)
    for item in findings:
        print(f"{item.target}: {item.path}: {item.message}", file=sys.stderr)
    if findings:
        return 1
    for project in projects:
        try:
            capabilities = (
                ",".join(projector.detected_project_capabilities(project)) or "none"
            )
        except (KeyError, OSError, TypeError, ValueError) as error:
            print(f"{project}: {error}", file=sys.stderr)
            return 1
        print(f"{project}\tcapabilities={capabilities}")
    return 0


def _adjust(root: Path, skill: str, apply: bool) -> int:
    try:
        directory = _catalog(root).record(skill).directory
    except (KeyError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    command = ["waza", "dev", str(directory)]
    command.extend(["--auto"] if apply else ["--copilot"])
    return run_command(command, root).exit_code


def _normalize(root: Path, apply: bool) -> int:
    try:
        changes = normalize(_catalog(root), apply=apply)
    except (OSError, KeyError, ValueError) as error:
        print(f"FAIL: normalization: {error}", file=sys.stderr)
        return 2
    for item in changes:
        print(
            f"{item.name}: {item.tokens} tokens/{item.lines} lines -> {item.destination}"
        )
    print(f"{'APPLIED' if apply else 'DRY-RUN'}: {len(changes)} skill(s)")
    return int(bool(changes) and not apply)


def _descriptions(root: Path, apply: bool) -> int:
    try:
        changes = normalize_descriptions(_catalog(root), apply=apply)
    except (OSError, KeyError, ValueError) as error:
        print(f"FAIL: descriptions: {error}", file=sys.stderr)
        return 2
    for item in changes:
        print(f"{item.name}: {item.destination}")
    print(f"{'APPLIED' if apply else 'DRY-RUN'}: {len(changes)} description(s)")
    return int(bool(changes) and not apply)


def _waza_artifact(root: Path, path: Path, destination: Path | None) -> int:
    try:
        artifact_kind = (
            publish_waza_artifact(root, path, destination)
            if destination is not None
            else validate_waza_artifact(root, path)
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"FAIL: invalid Waza artifact {path}: {error}", file=sys.stderr)
        return 1
    action = f"published atomically to {destination}" if destination else "validated"
    print(f"PASS: Waza {artifact_kind} artifact {action}: {path}")
    return 0


def _waza_model_catalog(root: Path, path: Path) -> int:
    try:
        model = validate_waza_model_catalog(root, path)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"FAIL: invalid Waza model catalog {path}: {error}", file=sys.stderr)
        return 1
    print(model)
    return 0


def _waza_coverage(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        total = payload.get("total_skills") if isinstance(payload, dict) else None
        covered = payload.get("covered") if isinstance(payload, dict) else None
        partial = payload.get("partial") if isinstance(payload, dict) else None
        uncovered = payload.get("uncovered") if isinstance(payload, dict) else None
        if not isinstance(total, int) or total <= 0:
            raise ValueError("coverage has no skills")
        if covered != total or partial != 0 or uncovered != 0:
            raise ValueError(
                f"coverage incomplete: {covered}/{total} covered, "
                f"{partial} partial, {uncovered} uncovered"
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: invalid Waza coverage artifact {path}: {error}", file=sys.stderr)
        return 1
    print(f"PASS: Waza eval coverage is {covered}/{total}")
    return 0


def _waza_config(root: Path, apply: bool, print_model: bool) -> int:
    try:
        model = waza_default_model(root)
        if print_model:
            print(model)
            return 0
        changes = apply_waza_config(root) if apply else waza_config_findings(root)
    except (ExceptionGroup, OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"FAIL: Waza configuration: {error}", file=sys.stderr)
        return 2
    for item in changes:
        relative = item.path.relative_to(root)
        print(f"{relative}: model {item.actual!r} -> {item.expected!r}")
    if changes and not apply:
        print(
            f"FAIL: {len(changes)} Waza eval model projection(s) drifted",
            file=sys.stderr,
        )
        return 1
    print(
        f"{'APPLIED' if apply else 'PASS'}: Waza model={model}; "
        f"{len(changes)} change(s)"
    )
    return 0


def _waza_preflight(root: Path) -> int:
    try:
        result = run_preflight(root)
    except (ExceptionGroup, OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"FAIL: Waza preflight: {error}", file=sys.stderr)
        return 2
    stream = sys.stdout if result.status == 0 else sys.stderr
    print(f"{result.status.name}: {result.message}", file=stream)
    return int(result.status)


def _clean(root: Path) -> int:
    try:
        removed = clean_generated(root)
    except (OSError, RuntimeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    for path in removed:
        print(f"REMOVED: {path}")
    print(f"PASS: cleaned {len(removed)} generated path(s)")
    return 0


def _temp_audit(root: Path, as_json: bool, global_scope: bool) -> int:
    items = (
        [*temp_global_findings(), *repository_findings(root)]
        if global_scope
        else repository_findings(root)
    )
    items = list(
        {
            (item.path, item.kind, item.message, item.size_bytes): item
            for item in items
        }.values()
    )
    items.sort(key=lambda item: str(item.path))
    blocking = [item for item in items if item.kind in {"prohibited", "residue"}]
    if as_json:
        print(
            json.dumps(
                [
                    {
                        "path": str(item.path),
                        "kind": item.kind,
                        "message": item.message,
                        "size_bytes": item.size_bytes,
                    }
                    for item in items
                ],
                indent=2,
                sort_keys=True,
            )
        )
        return int(bool(blocking))
    for item in items:
        print(
            f"{item.path}: {item.kind}: {item.message} ({item.size_bytes} bytes)",
            file=sys.stderr,
        )
    if blocking:
        print(
            f"FAIL: {len(blocking)} blocking temporary-filesystem finding(s)",
            file=sys.stderr,
        )
        return 1
    scope = "system and repository" if global_scope else "repository"
    print(f"PASS: no blocking temporary-filesystem findings in {scope} scope")
    return 0


def _temp_status(root: Path, as_json: bool) -> int:
    payload = temp_status(root)
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}\t{value}")
    return 0


def _temp_gc(root: Path, apply: bool, all_repositories: bool) -> int:
    eligible, blocked = (
        temp_gc_all(apply=apply) if all_repositories else temp_gc(root, apply=apply)
    )
    action = "REMOVED" if apply else "ELIGIBLE"
    for path in eligible:
        print(f"{action}: {path}")
    for item in blocked:
        print(f"{item.path}: {item.message}", file=sys.stderr)
    return 0


def _temp_global(as_json: bool) -> int:
    items = temp_global_findings()
    blocking = [item for item in items if item.kind in {"prohibited", "residue"}]
    if as_json:
        print(
            json.dumps(
                [
                    {
                        "path": str(item.path),
                        "kind": item.kind,
                        "message": item.message,
                        "size_bytes": item.size_bytes,
                    }
                    for item in items
                ],
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for item in items:
            print(f"{item.path}: {item.kind}: {item.message}")
    return int(bool(blocking))


def _temp_run(root: Path, command: list[str]) -> int:
    if command and command[0] == "--":
        command = command[1:]
    report = run_command(command, root)
    print(
        json.dumps(
            {
                "scratch": report.scratch,
                "scratch_retained": report.scratch_retained,
                "peak_bytes": report.peak_bytes,
                "exit_code": report.exit_code,
            }
        ),
        file=sys.stderr,
    )
    return report.exit_code


def _security_triage(roots: tuple[Path, ...], as_json: bool) -> int:
    findings = security_audit(roots)
    if as_json:
        print(
            json.dumps([item.as_dict() for item in findings], indent=2, sort_keys=True)
        )
    else:
        for item in findings:
            print(f"{item.path}: {item.code}: {item.message}", file=sys.stderr)
    if findings:
        print(
            f"FAIL: {len(findings)} blocking security triage finding(s)",
            file=sys.stderr,
        )
        return 1
    print("PASS: security triage is complete and evidenced")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="agentsctl")
    result.add_argument("--root", type=Path, default=_root())
    commands = result.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--write", action="store_true")
    validation = commands.add_parser("validate")
    validation.add_argument("--skill")
    command_surface = commands.add_parser("commands")
    command_actions = command_surface.add_subparsers(
        dest="command_action", required=True
    )
    command_actions.add_parser("audit")
    command_render = command_actions.add_parser("render")
    command_render.add_argument("slug")
    command_render.add_argument(
        "--provider",
        required=True,
        choices=tuple(provider.value for provider in CommandProvider),
    )
    command_render.add_argument("--max-tokens", type=int)
    projection = commands.add_parser("project")
    mode = projection.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    projection.add_argument("--target")
    projection.add_argument("--project-root", action="append", default=[], type=Path)
    projection.add_argument("--scope", choices=("personal", "projects"), required=True)
    projection.add_argument(
        "--surface", choices=("skills", "commands", "rules", "all"), default="all"
    )
    discovery = commands.add_parser("discover-projects")
    discovery.add_argument("--project-root", action="append", default=[], type=Path)
    adjust = commands.add_parser("adjust")
    adjust.add_argument("--skill", required=True)
    adjust.add_argument("--apply", action="store_true")
    normalization = commands.add_parser("normalize")
    normalization.add_argument("--apply", action="store_true")
    descriptions = commands.add_parser("descriptions")
    descriptions.add_argument("--apply", action="store_true")
    waza_artifact = commands.add_parser("waza-artifact")
    waza_artifact.add_argument("path", type=Path)
    waza_artifact.add_argument("--publish", type=Path)
    waza_model_catalog = commands.add_parser("waza-model-catalog")
    waza_model_catalog.add_argument("path", type=Path)
    waza_coverage = commands.add_parser("waza-coverage")
    waza_coverage.add_argument("path", type=Path)
    waza_config = commands.add_parser("waza-config")
    waza_config_mode = waza_config.add_mutually_exclusive_group(required=True)
    waza_config_mode.add_argument("--check", action="store_true")
    waza_config_mode.add_argument("--apply", action="store_true")
    waza_config_mode.add_argument("--model", action="store_true")
    commands.add_parser("waza-preflight")
    commands.add_parser("clean")
    temporary = commands.add_parser("temp")
    temp_commands = temporary.add_subparsers(dest="temp_command", required=True)
    temp_audit = temp_commands.add_parser("audit")
    temp_audit.add_argument("--json", action="store_true")
    temp_audit.add_argument("--global", dest="global_scope", action="store_true")
    temp_status_parser = temp_commands.add_parser("status")
    temp_status_parser.add_argument("--json", action="store_true")
    temp_run = temp_commands.add_parser("run")
    temp_run.add_argument("argv", nargs=argparse.REMAINDER)
    temp_gc_parser = temp_commands.add_parser("gc")
    temp_gc_parser.add_argument("--all", action="store_true")
    gc_mode = temp_gc_parser.add_mutually_exclusive_group(required=True)
    gc_mode.add_argument("--dry-run", action="store_true")
    gc_mode.add_argument("--apply", action="store_true")
    for name in ("inventory", "verify"):
        command = temp_commands.add_parser(name)
        command.add_argument("--global", dest="global_scope", action="store_true")
        command.add_argument("--json", action="store_true")
    security = commands.add_parser("security-triage")
    security.add_argument("roots", nargs="*", type=Path)
    security.add_argument("--json", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    if args.command == "audit":
        return _audit(root, args.write)
    if args.command == "validate":
        return _validate(root, args.skill)
    if args.command == "commands":
        if args.command_action == "audit":
            return _commands_audit(root)
        if args.command_action == "render":
            return _commands_render(root, args.slug, args.provider, args.max_tokens)
        raise AssertionError(args.command_action)
    if args.command == "project":
        return _project(
            root,
            args.apply,
            args.scope,
            args.target,
            args.surface,
            tuple(args.project_root),
        )
    if args.command == "discover-projects":
        return _discover_projects(root, tuple(args.project_root))
    if args.command == "adjust":
        return _adjust(root, args.skill, args.apply)
    if args.command == "normalize":
        return _normalize(root, args.apply)
    if args.command == "descriptions":
        return _descriptions(root, args.apply)
    if args.command == "waza-artifact":
        return _waza_artifact(root, args.path, args.publish)
    if args.command == "waza-model-catalog":
        return _waza_model_catalog(root, args.path)
    if args.command == "waza-coverage":
        return _waza_coverage(args.path)
    if args.command == "waza-config":
        return _waza_config(root, args.apply, args.model)
    if args.command == "waza-preflight":
        return _waza_preflight(root)
    if args.command == "clean":
        return _clean(root)
    if args.command == "temp":
        try:
            if args.temp_command == "audit":
                return _temp_audit(root, args.json, args.global_scope)
            if args.temp_command == "status":
                return _temp_status(root, args.json)
            if args.temp_command == "run":
                return _temp_run(Path.cwd().resolve(), args.argv)
            if args.temp_command == "gc":
                return _temp_gc(root, args.apply, args.all)
            if args.temp_command in {"inventory", "verify"}:
                if not args.global_scope:
                    raise ValueError("--global is required")
                return _temp_global(args.json)
            raise AssertionError(args.temp_command)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            print(f"FAIL: {error}", file=sys.stderr)
            return 2
    if args.command == "security-triage":
        roots = tuple(path.resolve() for path in args.roots) or (Path.cwd().resolve(),)
        return _security_triage(roots, args.json)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
