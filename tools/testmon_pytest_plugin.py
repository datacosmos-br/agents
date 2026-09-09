"""Emit strict pytest-testmon accounting for the canonical parent gate."""

from __future__ import annotations

import json
import os
import tempfile
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


@dataclass
class TestmonAuditPlugin:
    """Observe pytest/testmon without changing execution semantics."""

    config: pytest.Config
    mode: str
    report: Path
    executed: set[str] = field(default_factory=set)
    warnings: int = 0
    skips: int = 0
    xfails: int = 0

    def validate(self) -> None:
        """Require the active testmon plugin and exact execution mode."""

        tm_conf = cast(TestmonPytestConfig, self.config).testmon_config
        expected_select = self.mode == "incremental"
        if (
            not tm_conf.collect
            or tm_conf.select is not expected_select
            or tm_conf.tmnet
        ):
            raise RuntimeError(
                "testmon mode is not canonical: "
                f"collect={tm_conf.collect} select={tm_conf.select} tmnet={tm_conf.tmnet}"
            )
        for plugin in ("TestmonCollect", "TestmonSelect"):
            if not self.config.pluginmanager.hasplugin(plugin):
                raise RuntimeError(f"required testmon plugin is absent: {plugin}")

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
        plugin = self.config.pluginmanager.get_plugin("TestmonSelect")
        if plugin is None or not hasattr(plugin, "deselected_tests"):
            raise TypeError("TestmonSelect plugin has an unexpected type")
        deselected = (
            cast(TestmonSelectPlugin, plugin).deselected_tests
            if self.mode == "incremental"
            else []
        )
        document = {
            "executed": sorted(self.executed),
            "deselected": sorted(set(deselected)),
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
