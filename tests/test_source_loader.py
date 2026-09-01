from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from source_loader import load_source_module


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
