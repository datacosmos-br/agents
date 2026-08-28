import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({ name: "inventory", version: "1.0.0" });

server.tool("lookup", async (input: any) => {
  try {
    return await fetch(`https://inventory.invalid/${input.sku}`);
  } catch (error) {
    return { content: [{ type: "text", text: String(error.stack) }] };
  }
});

await server.connect(new StdioServerTransport());
