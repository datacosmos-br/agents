## Advanced FastMCP Features

### Context Parameter Injection

FastMCP can automatically inject a `Context` parameter into tools for advanced capabilities like logging, progress reporting, resource reading, and user interaction:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("example_mcp")


@mcp.tool()
async def advanced_search(query: str, ctx: Context) -> str:
    """Advanced tool with context access for logging and progress."""

    # Report progress for long operations
    await ctx.report_progress(0.25, "Starting search...")

    # Log information for debugging
    await ctx.log_info(
        "Processing query", {"query": query, "timestamp": datetime.now()}
    )

    # Perform search
    results = await search_api(query)
    await ctx.report_progress(0.75, "Formatting results...")

    # Access server configuration
    server_name = ctx.fastmcp.name

    return format_results(results)


@mcp.tool()
async def interactive_tool(resource_id: str, ctx: Context) -> str:
    """Tool that can request additional input from users."""

    # Request sensitive information when needed
    api_key = await ctx.elicit(
        prompt="Please provide your API key:", input_type="password"
    )

    # Use the provided key
    return await api_call(resource_id, api_key)
```

**Context capabilities:**
- `ctx.report_progress(progress, message)` - Report progress for long operations
- `ctx.log_info(message, data)` / `ctx.log_error()` / `ctx.log_debug()` - Logging
- `ctx.elicit(prompt, input_type)` - Request input from users
- `ctx.fastmcp.name` - Access server configuration
- `ctx.read_resource(uri)` - Read MCP resources

### Resource Registration

Expose data as resources for efficient, template-based access:

```python
@mcp.resource("file://documents/{name}")
async def get_document(name: str) -> str:
    """Expose documents as MCP resources.

    Resources are useful for static or semi-static data that doesn't
    require complex parameters. They use URI templates for flexible access.
    """
    document_path = f"./docs/{name}"
    with open(document_path, "r") as f:
        return f.read()


@mcp.resource("config://settings/{key}")
async def get_setting(key: str, ctx: Context) -> str:
    """Expose configuration as resources with context."""
    settings = await load_settings()
    return json.dumps(settings.get(key, {}))
```

**When to use Resources vs Tools:**
- **Resources**: For data access with simple parameters (URI templates)
- **Tools**: For complex operations with validation and business logic

### Structured Output Types

FastMCP supports multiple return types beyond strings:

```python
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel


# TypedDict for structured returns
class UserData(TypedDict):
    id: str
    name: str
    email: str


@mcp.tool()
async def get_user_typed(user_id: str) -> UserData:
    """Returns structured data - FastMCP handles serialization."""
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


# Pydantic models for complex validation
class DetailedUser(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    metadata: Dict[str, Any]


@mcp.tool()
async def get_user_detailed(user_id: str) -> DetailedUser:
    """Returns Pydantic model - automatically generates schema."""
    user = await fetch_user(user_id)
    return DetailedUser(**user)
```

### Lifespan Management

Initialize resources that persist across requests:

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def app_lifespan():
    """Manage resources that live for the server's lifetime."""
    # Initialize connections, load config, etc.
    db = await connect_to_database()
    config = load_configuration()

    # Make available to all tools
    yield {"db": db, "config": config}

    # Cleanup on shutdown
    await db.close()


mcp = FastMCP("example_mcp", lifespan=app_lifespan)


@mcp.tool()
async def query_data(query: str, ctx: Context) -> str:
    """Access lifespan resources through context."""
    db = ctx.request_context.lifespan_state["db"]
    results = await db.query(query)
    return format_results(results)
```

### Multiple Transport Options

FastMCP supports different transport mechanisms:

```python
# Default: Stdio transport (for CLI tools)
if __name__ == "__main__":
    mcp.run()

# HTTP transport (for web services)
if __name__ == "__main__":
    mcp.run(transport="streamable_http", port=8000)

# SSE transport (for real-time updates)
if __name__ == "__main__":
    mcp.run(transport="sse", port=8000)
```

**Transport selection:**
- **Stdio**: Command-line tools, subprocess integration
- **HTTP**: Web services, remote access, multiple clients
- **SSE**: Real-time updates, push notifications

---

## Code Best Practices

### Code Composability and Reusability

Your implementation MUST prioritize composability and code reuse:

1. **Extract Common Functionality**:
   - Create reusable helper functions for operations used across multiple tools
   - Build shared API clients for HTTP requests instead of duplicating code
   - Centralize error handling logic in utility functions
   - Extract business logic into dedicated functions that can be composed
   - Extract shared markdown or JSON field selection & formatting functionality

2. **Avoid Duplication**:
   - NEVER copy-paste similar code between tools
   - If you find yourself writing similar logic twice, extract it into a function
   - Common operations like pagination, filtering, field selection, and formatting should be shared
   - Authentication/authorization logic should be centralized

### Python-Specific Best Practices

1. **Use Type Hints**: Always include type annotations for function parameters and return values
2. **Pydantic Models**: Define clear Pydantic models for all input validation
3. **Avoid Manual Validation**: Let Pydantic handle input validation with constraints
4. **Proper Imports**: Group imports (standard library, third-party, local)
5. **Error Handling**: Use specific exception types (httpx.HTTPStatusError, not generic Exception)
6. **Async Context Managers**: Use `async with` for resources that need cleanup
7. **Constants**: Define module-level constants in UPPER_CASE
