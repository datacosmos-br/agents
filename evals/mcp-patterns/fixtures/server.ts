import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({ name: "inventory", version: "1.0.0" });

server.tool("lookup", async (input: any) => {
  return await fetch(`https://inventory.invalid/${input.sku}`);
});

await server.connect(new StdioServerTransport());
