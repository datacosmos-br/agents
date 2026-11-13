"""Real stdio MCP endpoint for optional metadata contract tests."""

from __future__ import annotations

import asyncio

from mcp.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp.types import ListToolsResult, PaginatedRequestParams, Tool


async def list_tools(
    ctx: ServerRequestContext[object], params: PaginatedRequestParams | None
) -> ListToolsResult:
    """Serve the three distinct metadata states allowed by the SDK."""
    del ctx, params
    return ListToolsResult(
        tools=[
            Tool(name="absent", input_schema={"type": "object"}),
            Tool(name="empty", description="", input_schema={"type": "object"}),
            Tool(
                name="described",
                description="Read metadata",
                input_schema={"type": "object"},
            ),
        ]
    )


server = Server("metadata-contract", on_list_tools=list_tools)


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
