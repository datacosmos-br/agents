"""Validate the same public helper import used by the evaluation resource."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from agents_governance import GovernanceBundle


def test_optional_tool_description_is_not_normalized(
    governance_bundle: GovernanceBundle, tmp_path: Path
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
    client = """import asyncio, json, sys
from connections import create_connection
async def main():
    async with create_connection(
        'stdio', command=sys.executable, args=[sys.argv[1]],
    ) as connection:
        print(json.dumps(await connection.list_tools()), flush=True)
asyncio.run(main())
"""
    result = subprocess.run(
        (sys.executable, "-c", client, str(server)),
        cwd=scripts,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    metadata = {tool["name"]: tool for tool in json.loads(result.stdout)}
    assert "description" not in metadata["absent"]
    assert metadata["empty"]["description"] == ""
    assert metadata["described"]["description"] == "Read metadata"
    assert "warning" not in result.stderr.lower()
