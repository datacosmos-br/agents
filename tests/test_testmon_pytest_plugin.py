"""Test-accounting contract of the root test verbs' pytest plugin."""

from __future__ import annotations

from pathlib import Path

import pytest
import testmon_pytest_plugin


def test_incremental_deselection_counts_items_and_placeholders(
    request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    audit = testmon_pytest_plugin.TestmonAuditPlugin(
        request.config, "incremental", tmp_path / "audit.json"
    )
    item = request.node
    assert isinstance(item, pytest.Item)

    audit.pytest_deselected([item, object(), object()])

    assert audit.deselected == {item.nodeid}
    assert audit.placeholders == 2


def test_full_deselection_rejects_entries_that_are_not_items(
    request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    audit = testmon_pytest_plugin.TestmonAuditPlugin(
        request.config, "full", tmp_path / "audit.json"
    )

    with pytest.raises(TypeError, match="not a pytest item"):
        audit.pytest_deselected([object()])


def test_testmon_names_cover_every_placeholder() -> None:
    names = ["tests/test_a.py::test_a", "tests/test_b.py::test_b"]

    assert testmon_pytest_plugin.account_testmon_deselection(names, 2) == set(names)


def test_placeholders_beyond_testmon_names_are_red() -> None:
    with pytest.raises(RuntimeError, match="deselected 2 items but named only 1"):
        testmon_pytest_plugin.account_testmon_deselection(
            ["tests/test_a.py::test_a"], 2
        )
