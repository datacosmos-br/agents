"""Lightweight connection handling for MCP servers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any

import httpx2
from mcp import ClientSession, StdioServerParameters
from mcp.client import Transport
from mcp.client.session_group import StreamableHttpParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

if TYPE_CHECKING:
    from anthropic.types import ToolParam


class MCPConnection(ABC):
    """Base class for MCP server connections."""

    def __init__(self) -> None:
        self.session: ClientSession | None = None
        self._stack: AsyncExitStack | None = None

    @abstractmethod
    async def _create_context(self, stack: AsyncExitStack) -> Transport:
        """Create the transport, entering every resource it borrows on ``stack``."""

    async def __aenter__(self):
        """Initialize MCP server connection."""
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        try:
            ctx = await self._create_context(self._stack)
            read, write = await self._stack.enter_async_context(ctx)

            session_ctx = ClientSession(read, write)
            self.session = await self._stack.enter_async_context(session_ctx)
            await self.session.initialize()
            return self
        except BaseException:
            await self._stack.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up MCP server connection resources."""
        if self._stack:
            await self._stack.__aexit__(exc_type, exc_val, exc_tb)
        self.session = None
        self._stack = None

    async def list_tools(self) -> list[ToolParam]:
        """Preserve supplied descriptions, omitting the optional field when absent."""
        if self.session is None:
            raise RuntimeError("MCP connection must be entered before listing tools")
        response = await self.session.list_tools()
        tools: list[ToolParam] = []
        for tool in response.tools:
            metadata: ToolParam = {
                "name": tool.name,
                "input_schema": tool.input_schema,
            }
            if tool.description is not None:
                metadata["description"] = tool.description
            tools.append(metadata)
        return tools

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the MCP server with provided arguments."""
        if self.session is None:
            raise RuntimeError("MCP connection must be entered before calling tools")
        result = await self.session.call_tool(tool_name, arguments=arguments)
        return result.content


class MCPConnectionStdio(MCPConnection):
    """MCP connection using standard input/output."""

    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.command = command
        self.args = args or []
        self.env = env

    async def _create_context(self, stack: AsyncExitStack) -> Transport:
        del stack
        return stdio_client(
            StdioServerParameters(command=self.command, args=self.args, env=self.env)
        )


class MCPConnectionSSE(MCPConnection):
    """MCP connection using Server-Sent Events."""

    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        super().__init__()
        self.url = url
        self.headers = headers or {}

    async def _create_context(self, stack: AsyncExitStack) -> Transport:
        del stack
        return sse_client(url=self.url, headers=self.headers)


class MCPConnectionHTTP(MCPConnection):
    """MCP connection using Streamable HTTP."""

    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        super().__init__()
        self.url = url
        self.headers = headers or {}

    async def _create_context(self, stack: AsyncExitStack) -> Transport:
        # The SDK configures headers through a caller-owned client; its timeouts
        # come from the SDK's own streamable HTTP parameter defaults.
        params = StreamableHttpParameters(url=self.url, headers=self.headers)
        client = await stack.enter_async_context(
            httpx2.AsyncClient(
                headers=params.headers,
                timeout=httpx2.Timeout(params.timeout, read=params.sse_read_timeout),
            )
        )
        return streamable_http_client(params.url, http_client=client)


def create_connection(
    transport: str,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    url: str | None = None,
    headers: dict[str, str] | None = None,
) -> MCPConnection:
    """Factory function to create the appropriate MCP connection.

    Args:
        transport: Connection type ("stdio", "sse", or "http")
        command: Command to run (stdio only)
        args: Command arguments (stdio only)
        env: Environment variables (stdio only)
        url: Server URL (sse and http only)
        headers: HTTP headers (sse and http only)

    Returns:
        MCPConnection instance

    """
    transport = transport.lower()

    if transport == "stdio":
        if not command:
            msg = "Command is required for stdio transport"
            raise ValueError(msg)
        return MCPConnectionStdio(command=command, args=args, env=env)

    if transport == "sse":
        if not url:
            msg = "URL is required for sse transport"
            raise ValueError(msg)
        return MCPConnectionSSE(url=url, headers=headers)

    if transport in {"http", "streamable_http", "streamable-http"}:
        if not url:
            msg = "URL is required for http transport"
            raise ValueError(msg)
        return MCPConnectionHTTP(url=url, headers=headers)

    msg = f"Unsupported transport type: {transport}. Use 'stdio', 'sse', or 'http'"
    raise ValueError(msg)
