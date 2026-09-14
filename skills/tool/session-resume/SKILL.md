---
name: session-resume
description: 'session source detection, handoff cross-check, unfinished step resume'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:claude","detect:opt-in:opencode","detect:opt-in:poolside","effective:2026-09-06","route:agent","subject:agents","usage:router"]'
---

# Session Resume

Activate when the user wants to resume execution from a previous session.
Supports both Poolside and Claude Code session formats.

## Source Detection

The skill auto-detects session source from the ID format:

| Source | ID Format | Example |
|---|---|---|
| Poolside | UUID v7 | `01a07966-03e0-7df3-bf3b-dde492feabd8` |
| Claude | UUID v4 | `08f1115d-dd1b-4da1-bf60-0a337b29f5ef` |
| OpenCode | `ses_` prefix | `ses_f8b25a89effeXKTKUYNMf01TkN` |

## Resume Procedure

### 1. Detect source and locate session

```bash
SESSION_ID="<session-id>"

# Poolside: check logs
if ls ~/.local/state/poolside/pool/logs/*/$SESSION_ID 2>/dev/null; then
    SOURCE="poolside"
fi

# Claude: check projects
if grep -q "$SESSION_ID" ~/.claude/history.jsonl 2>/dev/null; then
    SOURCE="claude"
fi

# OpenCode: check database
if opencode export "$SESSION_ID" 2>/dev/null; then
    SOURCE="opencode"
fi
```

### 2. Extract session based on source

```bash
case "$SOURCE" in
    poolside)
        python3 <catalog>/skills/tool/poolside-session-extract/scripts/extract_poolside_session.py "$SESSION_ID"
        ;;
    claude)
        python3 <catalog>/skills/tool/claude-session-extract/scripts/extract_claude_session.py "$SESSION_ID"
        ;;
    opencode)
        python3 <catalog>/skills/agent-wide/personal/opencode-handoff/scripts/export_session_snapshot.py "$SESSION_ID"
        ;;
esac
```

### 3. Read extracted handoff

```bash
# Find the handoff file
HANDOFF=$(find ~/.local/state -name "handoff.sanitised.md" -path "*$SESSION_ID*" 2>/dev/null | head -1)
cat "$HANDOFF"
```

### 4. Cross-check and reconstruct cursor

Read the handoff and verify against current state:
- Original objective and newest operator correction
- Persisted plan and first unfinished step
- Last successful and failed commands
- Repositories and paths changed
- Branch, HEAD, worktree changes

### 5. Continue execution

Based on the handoff, continue from the first unfinished step.
Apply the operator's latest instructions and current repository state.

## Output Locations

| Source | Export Directory |
|---|---|
| Poolside | `~/.local/state/poolside/exports/<session-id>/` |
| Claude | `~/.local/state/claude/exports/<session-id>/` |
| OpenCode | `<opencode-data-root>/exports/<session-id>/` |

## Secret Redaction

All extraction scripts redact credential-shaped values before output.
Private logs are stored with mode 0600.

## Precedence

Operator request > this skill > default.
