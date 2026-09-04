from __future__ import annotations

import ast
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from source_loader import load_source_module

SCRIPT_EXECUTABLE_ALLOWLISTS = {
    "skills/agent-wide/personal/opencode-session-handoff/scripts/export_session_snapshot.py": {
        "opencode"
    },
    "skills/domain/gascity/mayor/assets/scripts/create_beads_from_tasks.py": {"gc"},
    "skills/tool/pr-sheriff/scripts/pr_triage.py": {"gh", "git"},
}


def test_projected_skill_scripts_are_stdlib_only_with_exact_allowlists() -> None:
    root = Path(__file__).parents[1]
    scripts = sorted(root.glob("skills/**/scripts/*.py"))
    assert {str(path.relative_to(root)) for path in scripts} == set(
        SCRIPT_EXECUTABLE_ALLOWLISTS
    )
    for script in scripts:
        tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        imports = {
            alias.name.partition(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.partition(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert imports <= sys.stdlib_module_names
        module = load_source_module(f"isolated_{script.stem}", script)
        assert module.EXTERNAL_EXECUTABLES == frozenset(
            SCRIPT_EXECUTABLE_ALLOWLISTS[str(script.relative_to(root))]
        )


def test_catalog_script_loading_does_not_inherit_caller_future_flags(
    tmp_path: Path,
) -> None:
    source = tmp_path / "catalog_script.py"
    source.write_text("value = 1\n", encoding="utf-8")
    compiler = compile

    with patch("builtins.compile", wraps=compiler) as compile_mock:
        load_source_module("runtime_annotations", source)

    compile_mock.assert_called_once_with(
        b"value = 1\n", str(source), "exec", dont_inherit=True
    )


def test_catalog_script_loading_is_concurrent_and_residue_free() -> None:
    root = Path(__file__).parents[1]
    sources = (
        root
        / "skills/agent-wide/personal/opencode-session-handoff/scripts/export_session_snapshot.py",
        root / "skills/tool/pr-sheriff/scripts/pr_triage.py",
    )
    before = tuple(source.parent.glob("__pycache__/*.pyc") for source in sources)
    assert all(not tuple(paths) for paths in before)

    with ThreadPoolExecutor(max_workers=8) as executor:
        loaded = tuple(
            executor.map(
                lambda item: load_source_module(f"catalog_script_{item[0]}", item[1]),
                enumerate(sources * 8),
            )
        )

    assert len(loaded) == 16
    assert all(not tuple(source.parent.glob("__pycache__/*.pyc")) for source in sources)
