"""Validate the same public helper import used by the evaluation resource."""

from __future__ import annotations

import asyncio
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

from agents_governance import GovernanceBundle


def test_optional_tool_description_is_not_normalized(
    governance_bundle: GovernanceBundle,
    tmp_path: Path,
    capfd: pytest.CaptureFixture[str],
) -> None:
    skill = next(
        item for item in governance_bundle.skills if item.name == "mcp-builder"
    )
    resource = next(
        item for item in skill.resources if item.path.name == "connections.py"
    )
    server = Path(__file__).parent / "fixtures" / "mcp_metadata_server.py"
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    staged = scripts / resource.path.name
    shutil.copy2(resource.path, staged)
    assert staged.read_bytes() == resource.path.read_bytes()
    spec = importlib.util.spec_from_file_location("connections", staged)
    assert spec is not None and spec.loader is not None
    connections = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connections)

    async def list_metadata() -> list[dict[str, object]]:
        async with (
            asyncio.timeout(20),
            connections.create_connection(
                "stdio", command=sys.executable, args=[str(server)]
            ) as connection,
        ):
            return await connection.list_tools()

    metadata = {tool["name"]: tool for tool in asyncio.run(list_metadata())}
    assert "description" not in metadata["absent"]
    assert metadata["empty"]["description"] == ""
    assert metadata["described"]["description"] == "Read metadata"
    assert "warning" not in capfd.readouterr().err.lower()
