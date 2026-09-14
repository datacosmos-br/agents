"""Lightweight connection handling for MCP servers."""

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from typing import Any

from anthropic.types import ToolParam
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import GetSessionIdCallback, streamablehttp_client
from mcp.shared.message import SessionMessage

type TransportStreams = (
    tuple[
        MemoryObjectReceiveStream[SessionMessage | Exception],
        MemoryObjectSendStream[SessionMessage],
    ]
    | tuple[
        MemoryObjectReceiveStream[SessionMessage | Exception],
        MemoryObjectSendStream[SessionMessage],
        GetSessionIdCallback,
    ]
)


class MCPConnection(ABC):
    """Base class for MCP server connections."""

    def __init__(self) -> None:
        self.session: ClientSession | None = None
        self._stack: AsyncExitStack | None = None

    @abstractmethod
    def _create_context(self) -> AbstractAsyncContextManager[TransportStreams]:
        """Create the connection context based on connection type."""

    async def __aenter__(self):
        """Initialize MCP server connection."""
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        try:
            ctx = self._create_context()
            result = await self._stack.enter_async_context(ctx)

            if len(result) == 2:
                read, write = result
            elif len(result) == 3:
                read, write, _ = result
            else:
                msg = f"Unexpected context result: {result}"
                raise ValueError(msg)

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
        """Retrieve available tools from the MCP server."""
        if self.session is None:
            raise RuntimeError("MCP connection must be entered before listing tools")
        response = await self.session.list_tools()
        tools: list[ToolParam] = []
        for tool in response.tools:
            metadata: ToolParam = {
                "name": tool.name,
                "input_schema": tool.inputSchema,
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

    def _create_context(self):
        return stdio_client(
            StdioServerParameters(command=self.command, args=self.args, env=self.env)
        )


class MCPConnectionSSE(MCPConnection):
    """MCP connection using Server-Sent Events."""

    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        super().__init__()
        self.url = url
        self.headers = headers or {}

    def _create_context(self):
        return sse_client(url=self.url, headers=self.headers)


class MCPConnectionHTTP(MCPConnection):
    """MCP connection using Streamable HTTP."""

    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        super().__init__()
        self.url = url
        self.headers = headers or {}

    def _create_context(self):
        return streamablehttp_client(url=self.url, headers=self.headers)


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
