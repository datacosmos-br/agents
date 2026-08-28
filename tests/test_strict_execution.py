from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "agents_governance"
EXCEPTION_OWNERS = {"atomic_io.py", "cleanup.py"}


def _source_trees() -> tuple[tuple[Path, ast.Module], ...]:
    return tuple(
        (path, ast.parse(path.read_text(encoding="utf-8")))
        for path in sorted(SOURCE.glob("*.py"))
    )


def _call_name(node: ast.Call) -> str | None:
    function = node.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return None


def test_only_cleanup_and_rollback_owners_catch_exceptions() -> None:
    violations = tuple(
        f"{path.name}:{node.lineno}"
        for path, tree in _source_trees()
        if path.name not in EXCEPTION_OWNERS
        for node in ast.walk(tree)
        if isinstance(node, (ast.Try, ast.TryStar))
    )

    assert violations == ()


def test_child_process_failures_are_never_normalized() -> None:
    violations: list[str] = []
    for path, tree in _source_trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or _call_name(node) not in {
                "run",
                "call",
                "Popen",
            }:
                continue
            check = next(
                (keyword.value for keyword in node.keywords if keyword.arg == "check"),
                None,
            )
            if isinstance(check, ast.Constant) and check.value is False:
                violations.append(f"{path.name}:{node.lineno}")

    assert tuple(violations) == ()


def test_runtime_has_no_finding_or_operational_default_protocol() -> None:
    violations: list[str] = []
    for path, tree in _source_trees():
        for node in ast.walk(tree):
            if (
                isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                and "finding" in node.name.casefold()
            ):
                violations.append(f"{path.name}:{node.lineno}:{node.name}")
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            if name in {"getenv", "setdefault", "warn", "warning"}:
                violations.append(f"{path.name}:{node.lineno}:{name}")
            if (
                name == "get"
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "os"
                and node.func.value.attr == "environ"
            ):
                violations.append(f"{path.name}:{node.lineno}:environ.get")

    assert tuple(violations) == ()
