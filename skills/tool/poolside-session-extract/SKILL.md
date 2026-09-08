---
name: poolside-session-extract
description: 'poolside trajectory extraction, conversation flow, sanitised handoff resume'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:poolside","effective:2026-09-06","route:agent","subject:agents","usage:router"]'
---

# Poolside Session Extract

Activate when the user requests to extract, view, or resume a Poolside session.
Converts NDJSON trajectory files into readable markdown summaries with full conversation flow.

## Storage Locations

| Component | Path | Description |
|---|---|---|
| Trajectories | `~/.local/state/poolside/trajectories/trajectory-standalone_<session_id>.ndjson` | Full event log (NDJSON) |
| Session metadata | `~/.local/state/poolside/sessions/session-<session_id>.json` | Run ID, agent ID, timestamps |
| ACP logs | `~/.local/state/poolside/pool/logs/<workspace>/<session_id>/acp.log.jsonl` | ACP protocol events |
| TUI logs | `~/.local/state/poolside/pool/logs/<workspace>/<session_id>/tui.log.jsonl` | TUI UI events |
| Prompt history | `~/.local/state/poolside/pool/<workspace_hash>/prompt-history.json` | Per-workspace prompt cache |

## Extraction Procedure

### 1. Run the extractor script

```bash
python3 ~/.agents/skills/tool/poolside-session-extract/scripts/extract_poolside_session.py <session-id>
```

Output goes to `~/.local/state/poolside/exports/<session-id>/`.

### 2. Output files

| File | Description |
|---|---|
| `handoff.sanitised.md` | Readable conversation summary with tool calls, results, reasoning |
| `conversation.private.json` | Structured conversation turns for programmatic use |
| `manifest.json` | SHA-256 digests and metadata |
| `trajectory.private.jsonl` | Raw trajectory (private) |
| `acp-log.private.jsonl` | Raw ACP log (private) |
| `tui-log.private.jsonl` | Raw TUI log (private) |

### 3. What the conversation flow captures

Each turn in the conversation flow includes:

- **User prompts** — with mode (build/apply) and timestamp
- **Tool calls** — tool name, parsed arguments (bash commands shown as code blocks)
- **Tool results** — observation output, success/failure status
- **Reasoning** — LLM thought blocks from `thought.end` events

### 4. Resume Integration

To continue execution from an extracted session, use the `session-resume` skill
with the generated summary as input context.

## Secret Redaction

The extraction script redacts credential-shaped values (authorization, api_key,
token, password, secret, cookie, bearer) in all output.
