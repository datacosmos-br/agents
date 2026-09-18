"""Real stdio MCP endpoint for optional metadata contract tests."""

from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

server = Server("metadata-contract")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Serve the three distinct metadata states allowed by the SDK."""
    return [
        Tool(name="absent", inputSchema={"type": "object"}),
        Tool(name="empty", description="", inputSchema={"type": "object"}),
        Tool(
            name="described",
            description="Read metadata",
            inputSchema={"type": "object"},
        ),
    ]


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
