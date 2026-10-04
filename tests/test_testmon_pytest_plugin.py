"""Test-accounting contract of the root test verbs' pytest plugin."""

from __future__ import annotations

from pathlib import Path

import pytest
import testmon_pytest_plugin


def test_incremental_deselection_counts_items_and_accepts_testmon_placeholders(
    request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    audit = testmon_pytest_plugin.TestmonAuditPlugin(
        request.config, "incremental", tmp_path / "audit.json"
    )
    item = request.node
    assert isinstance(item, pytest.Item)

    audit.pytest_deselected([item, object()])

    assert audit.deselected == {item.nodeid}


def test_full_deselection_rejects_entries_that_are_not_items(
    request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    audit = testmon_pytest_plugin.TestmonAuditPlugin(
        request.config, "full", tmp_path / "audit.json"
    )

    with pytest.raises(TypeError, match="not a pytest item"):
        audit.pytest_deselected([object()])
