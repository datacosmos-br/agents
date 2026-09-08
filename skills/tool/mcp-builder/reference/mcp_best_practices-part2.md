## 7. Tool Development Best Practices

### General Guidelines
1. Tool names should be descriptive and action-oriented
2. Use parameter validation with detailed JSON schemas
3. Include examples in tool descriptions
4. Implement proper error handling and validation
5. Use progress reporting for long operations
6. Keep tool operations focused and atomic
7. Document expected return value structures
8. Implement proper timeouts
9. Consider rate limiting for resource-intensive operations
10. Log tool usage for debugging and monitoring

### Security Considerations for Tools

#### Input Validation
- Validate all parameters against schema
- Sanitize file paths and system commands
- Validate URLs and external identifiers
- Check parameter sizes and ranges
- Prevent command injection

#### Access Control
- Implement authentication where needed
- Use appropriate authorization checks
- Audit tool usage
- Rate limit requests
- Monitor for abuse

#### Error Handling
- Don't expose internal errors to clients
- Log security-relevant errors
- Handle timeouts appropriately
- Clean up resources after errors
- Validate return values

### Tool Annotations
- Provide readOnlyHint and destructiveHint annotations
- Remember annotations are hints, not security guarantees
- Clients should not make security-critical decisions based solely on annotations

---

## 8. Transport Best Practices

### General Transport Guidelines
1. Handle connection lifecycle properly
2. Implement proper error handling
3. Use appropriate timeout values
4. Implement connection state management
5. Clean up resources on disconnection

### Security Best Practices for Transport
- Follow security considerations for DNS rebinding attacks
- Implement proper authentication mechanisms
- Validate message formats
- Handle malformed messages gracefully

### Stdio Transport Specific
- Local MCP servers should NOT log to stdout (interferes with protocol)
- Use stderr for logging messages
- Handle standard I/O streams properly

---

## 9. Testing Requirements

A comprehensive testing strategy should cover:

### Functional Testing
- Verify correct execution with valid/invalid inputs

### Integration Testing
- Test interaction with external systems

### Security Testing
- Validate auth, input sanitization, rate limiting

### Performance Testing
- Check behavior under load, timeouts

### Error Handling
- Ensure proper error reporting and cleanup

---

## 10. OAuth and Security Best Practices

### Authentication and Authorization

MCP servers that connect to external services should implement proper authentication:

**OAuth 2.1 Implementation:**
- Use secure OAuth 2.1 with certificates from recognized authorities
- Validate access tokens before processing requests
- Only accept tokens specifically intended for your server
- Reject tokens without proper audience claims
- Never pass through tokens received from MCP clients

**API Key Management:**
- Store API keys in environment variables, never in code
- Validate keys on server startup
- Provide clear error messages when authentication fails
- Use secure transmission for sensitive credentials

### Input Validation and Security

**Always validate inputs:**
- Sanitize file paths to prevent directory traversal
- Validate URLs and external identifiers
- Check parameter sizes and ranges
- Prevent command injection in system calls
- Use schema validation (Pydantic/Zod) for all inputs

**Error handling security:**
- Don't expose internal errors to clients
- Log security-relevant errors server-side
- Provide helpful but not revealing error messages
- Clean up resources after errors

### Privacy and Data Protection

**Data collection principles:**
- Only collect data strictly necessary for functionality
- Don't collect extraneous conversation data
- Don't collect PII unless explicitly required for the tool's purpose
- Provide clear information about what data is accessed

**Data transmission:**
- Don't send data to servers outside your organization without disclosure
- Use secure transmission (HTTPS) for all network communication
- Validate certificates for external services

---

## 11. Resource Management Best Practices

1. Only suggest necessary resources
2. Use clear, descriptive names for roots
3. Handle resource boundaries properly
4. Respect client control over resources
5. Use model-controlled primitives (tools) for automatic data exposure

---

## 12. Prompt Management Best Practices

- Clients should show users proposed prompts
- Users should be able to modify or reject prompts
- Clients should show users completions
- Users should be able to modify or reject completions
- Consider costs when using sampling

---

## 13. Error Handling Standards

- Use standard JSON-RPC error codes
- Report tool errors within result objects (not protocol-level)
- Provide helpful, specific error messages
- Don't expose internal implementation details
- Clean up resources properly on errors

---

## 14. Documentation Requirements

- Provide clear documentation of all tools and capabilities
- Include working examples (at least 3 per major feature)
- Document security considerations
- Specify required permissions and access levels
- Document rate limits and performance characteristics

---

## 15. Compliance and Monitoring

- Implement logging for debugging and monitoring
- Track tool usage patterns
- Monitor for potential abuse
- Maintain audit trails for security-relevant operations
- Be prepared for ongoing compliance reviews

---

## Summary

These best practices represent the comprehensive guidelines for building secure, efficient, and compliant MCP servers that work well within the ecosystem. Developers should follow these guidelines to ensure their MCP servers meet the standards for inclusion in the MCP directory and provide a safe, reliable experience for users.


----------


# Tools

> Enable LLMs to perform actions through your server

Tools are a powerful primitive in the Model Context Protocol (MCP) that enable servers to expose executable functionality to clients. Through tools, LLMs can interact with external systems, perform computations, and take actions in the real world.

<Note>
  Tools are designed to be **model-controlled**, meaning that tools are exposed from servers to clients with the intention of the AI model being able to automatically invoke them (with a human in the loop to grant approval).
</Note>

## Overview

Tools in MCP allow servers to expose executable functions that can be invoked by clients and used by LLMs to perform actions. Key aspects of tools include:

* **Discovery**: Clients can obtain a list of available tools by sending a `tools/list` request
* **Invocation**: Tools are called using the `tools/call` request, where servers perform the requested operation and return results
* **Flexibility**: Tools can range from simple calculations to complex API interactions

Like [resources](https://modelcontextprotocol.io/docs/concepts/resources), tools are identified by unique names and can include descriptions to guide their usage. However, unlike resources, tools represent dynamic operations that can modify state or interact with external systems.

## Tool definition structure

Each tool is defined with the following structure:

```typescript
{
  name: string;          // Unique identifier for the tool
  description?: string;  // Human-readable description
  inputSchema: {         // JSON Schema for the tool's parameters
    type: "object",
    properties: { ... }  // Tool-specific parameters
  },
  annotations?: {        // Optional hints about tool behavior
    title?: string;      // Human-readable title for the tool
    readOnlyHint?: boolean;    // If true, the tool does not modify its environment
    destructiveHint?: boolean; // If true, the tool may perform destructive updates
    idempotentHint?: boolean;  // If true, repeated calls with same args have no additional effect
    openWorldHint?: boolean;   // If true, tool interacts with external entities
  }
}
```
