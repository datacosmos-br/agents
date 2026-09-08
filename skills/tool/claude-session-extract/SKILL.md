---
name: claude-session-extract
description: 'claude session extraction, conversation flow, sanitised handoff resume'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:claude","effective:2026-09-06","route:agent","subject:agents","usage:router"]'
---

# Claude Session Extract

Activate when the user requests to extract, view, or resume a Claude Code session.
Converts JSONL session files into readable markdown summaries with full conversation flow.

## Storage Locations

| Component | Path | Description |
|---|---|---|
| Session history | `~/.claude/history.jsonl` | Main index of all sessions |
| Session data | `~/.claude/projects/<project-hash>/<session-id>.jsonl` | Full conversation (NDJSON) |
| Subagents | `~/.claude/projects/<project-hash>/<session-id>/subagents/` | Subagent metadata |
| Tool results | `~/.claude/projects/<project-hash>/<session-id>/tool-results/` | Tool output files |

## Extraction Procedure

### 1. Run the extractor script

```bash
python3 ~/.agents/skills/tool/claude-session-extract/scripts/extract_claude_session.py <session-id>
```

Output goes to `~/.local/state/claude/exports/<session-id>/`.

### 2. Output files

| File | Description |
|---|---|
| `handoff.sanitised.md` | Readable conversation summary with tool calls, results, reasoning |
| `conversation.private.json` | Structured conversation turns for programmatic use |
| `manifest.json` | SHA-256 digests and metadata |

### 3. What the conversation flow captures

Each turn in the conversation flow includes:

- **User messages** — with timestamps, including tool_result wrappers
- **Tool calls** — tool name, parsed arguments (bash commands shown as code blocks)
- **Tool results** — observation output matched to their tool_use_id
- **Reasoning** — thinking blocks from the assistant
- **Assistant text** — natural language responses

### 4. Resume Integration

To continue execution from an extracted session:

```bash
claude --resume <session-id>
```

Or use the `session-resume` skill with the generated summary as input context.

## Secret Redaction

The extraction script redacts credential-shaped values (authorization, api_key,
token, password, secret, cookie, bearer) in all output.
