"""Emit strict test accounting for the canonical root test verbs."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, cast

import pytest


class TestmonSettings(Protocol):
    """Settings surfaced by the active pytest-testmon plugin."""

    collect: bool
    select: bool
    tmnet: bool


class TestmonPytestConfig(Protocol):
    """Typed pytest extension installed by pytest-testmon."""

    testmon_config: TestmonSettings


class TestmonSelectPlugin(Protocol):
    """Selection evidence surfaced by pytest-testmon."""

    deselected_tests: list[str]


class WarningMessage(Protocol):
    """Warning record supplied by pytest's public hook."""

    message: Warning
    category: type[Warning]
    filename: str
    lineno: int


_TESTMON_PLUGINS = ("TestmonCollect", "TestmonSelect")


@dataclass
class TestmonAuditPlugin:
    """Observe pytest/testmon without changing execution semantics.

    ``incremental`` (``make test``) requires active testmon collection and
    selection; ``full`` (``make test-full``) requires testmon to be inactive.
    """

    config: pytest.Config
    mode: str
    report: Path
    collected: set[str] = field(default_factory=set)
    executed: set[str] = field(default_factory=set)
    deselected: set[str] = field(default_factory=set)
    warnings: int = 0
    skips: int = 0
    xfails: int = 0

    def validate(self) -> None:
        """Require the exact testmon state of the selected root test verb."""

        tm_conf = cast(TestmonPytestConfig, self.config).testmon_config
        active = self.mode == "incremental"
        if (
            tm_conf.collect is not active
            or tm_conf.select is not active
            or tm_conf.tmnet
        ):
            raise RuntimeError(
                f"testmon state is not canonical for {self.mode}: "
                f"collect={tm_conf.collect} select={tm_conf.select} tmnet={tm_conf.tmnet}"
            )
        for plugin in _TESTMON_PLUGINS:
            if self.config.pluginmanager.hasplugin(plugin) is not active:
                raise RuntimeError(
                    f"testmon plugin {plugin} presence is not canonical for {self.mode}"
                )

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        self.collected = {item.nodeid for item in session.items}

    def pytest_deselected(self, items: Sequence[pytest.Item]) -> None:
        self.deselected.update(item.nodeid for item in items)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when == "call":
            self.executed.add(report.nodeid)
        if report.skipped:
            self.skips += 1
        if hasattr(report, "wasxfail"):
            self.xfails += 1

    def pytest_warning_recorded(
        self,
        warning_message: WarningMessage,
        when: str,
        nodeid: str,
        location: tuple[str, int, str] | None,
    ) -> None:
        del warning_message, when, nodeid, location
        self.warnings += 1

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self) -> None:
        deselected = set(self.deselected)
        if self.mode == "incremental":
            plugin = self.config.pluginmanager.get_plugin("TestmonSelect")
            if plugin is None or not hasattr(plugin, "deselected_tests"):
                raise TypeError("TestmonSelect plugin has an unexpected type")
            deselected.update(cast(TestmonSelectPlugin, plugin).deselected_tests)
        document = {
            "collected": sorted(self.collected),
            "executed": sorted(self.executed),
            "deselected": sorted(deselected),
            "warnings": self.warnings,
            "skips": self.skips,
            "xfails": self.xfails,
        }
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=".testmon-audit-",
            dir=self.report.parent,
            delete=False,
        ) as staged:
            json.dump(document, staged, sort_keys=True)
            staged.write("\n")
            staged.flush()
            os.fsync(staged.fileno())
            staged_path = Path(staged.name)
        staged_path.replace(self.report)


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """Wire one audit instance at pytest's executable composition edge."""

    mode = os.environ.get("TESTMON_MODE")
    if mode not in {"full", "incremental"}:
        raise ValueError("TESTMON_MODE must equal full or incremental")
    configured = os.environ.get("TESTMON_AUDIT_PATH")
    if configured is None:
        raise ValueError("TESTMON_AUDIT_PATH is required")
    report = Path(configured)
    if not report.is_absolute() or report.exists() or report.is_symlink():
        raise ValueError("TESTMON_AUDIT_PATH must be a new absolute path")
    plugin = TestmonAuditPlugin(config, mode, report)
    plugin.validate()
    config.pluginmanager.register(plugin, "agents-testmon-audit")
