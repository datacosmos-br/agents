---
name: mcp-patterns
description: 'mcp servers, protocol integration, sdk patterns'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:dependency:npm:@modelcontextprotocol/sdk","detect:dependency:python:mcp","effective:2026-08-28","route:project","subject:mcp","supersedes:skill:mcp-server-patterns","usage:on-demand"]'
---

# MCP Server Patterns

Activate only when a detected MCP SDK is being built, changed, or debugged.
Before editing, read the pinned package and lock evidence, installed SDK surface,
existing server and clients, protocol capabilities, transports, and exact
official documentation for that version. Never guess a signature, upgrade,
transport, or compatibility requirement.

Preserve semantic ownership: tools perform declared actions, resources expose
read-only data, prompts expose templates, and transports adapt the same handlers.
Define and validate complete input/output schemas. For an effectful handler,
validate request, authorization, non-derivable current-process credentials,
cost, and publication boundary before the first effect.

Use one pinned SDK interface and only the transports required by current
consumers. Do not add legacy transport, local adapter, alternate SDK, keyring,
profiles, retry, or error-as-content normalization. Handlers do not catch causal
workflow failures; the pinned SDK transport owns protocol serialization without
changing the first cause. Child nonzero exit, timeout, signal, or incomplete
publication propagates unchanged.

Validate each declared consumer transport through the project's native test
owner. Publish server state atomically and remove partial artifacts on failure.
