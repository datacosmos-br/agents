# Session Management

Run multiple isolated browser sessions concurrently with state persistence.

## Named Sessions

Use `--session` flag to isolate browser contexts:

```bash
# Session 1: Authentication flow
agent-browser --session auth open https://app.example.com/login

# Session 2: Public browsing (separate cookies, storage)
agent-browser --session public open https://example.com

# Commands are isolated by session
agent-browser --session auth fill @e1 "user@example.com"
agent-browser --session public get text body
```

## Session Isolation Properties

Each session has independent:
- Cookies
- LocalStorage / SessionStorage
- IndexedDB
- Cache
- Browsing history
- Open tabs

## Session State Persistence

### Save Session State

```bash
# Save cookies, storage, and auth state
agent-browser state save /path/to/auth-state.json
```

### Load Session State

```bash
# Restore saved state
agent-browser state load /path/to/auth-state.json

# Continue with authenticated session
agent-browser open https://app.example.com/dashboard
```

### State File Contents

```json
{
  "cookies": [...],
  "localStorage": {...},
  "sessionStorage": {...},
  "origins": [...]
}
```

## Common Patterns

### Authenticated Session Reuse

```bash
#!/bin/bash
# Reuse a previously validated login state
set -euo pipefail

STATE_FILE="${XDG_STATE_HOME:-$HOME/.local/state}/agent-browser/auth-state.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: authentication state does not exist" >&2
    exit 1
fi

agent-browser state load "$STATE_FILE"
agent-browser open https://app.example.com/dashboard
current_url="$(agent-browser get url)"
if [[ "$current_url" != "https://app.example.com/dashboard"* ]]; then
    echo "ERROR: restored state did not reach the expected protected route" >&2
    exit 1
fi
```

### Concurrent Scraping

```bash
#!/bin/bash
# Scrape multiple sites concurrently
set -euo pipefail

sessions=(site1 site2 site3)
cleanup() {
    local operation_status=$?
    local cleanup_status=0
    local session_status=0

    trap - EXIT
    for session in "${sessions[@]}"; do
        session_status=0
        agent-browser --session "$session" close || session_status=$?
        if (( cleanup_status == 0 && session_status != 0 )); then
            cleanup_status=$session_status
        fi
    done
    if (( operation_status != 0 )); then
        exit "$operation_status"
    fi
    exit "$cleanup_status"
}
trap cleanup EXIT

# Start all sessions
agent-browser --session site1 open https://site1.com &
site1_pid=$!
agent-browser --session site2 open https://site2.com &
site2_pid=$!
agent-browser --session site3 open https://site3.com &
site3_pid=$!

first_status=0
for pid in "$site1_pid" "$site2_pid" "$site3_pid"; do
    child_status=0
    wait "$pid" || child_status=$?
    if (( first_status == 0 && child_status != 0 )); then
        first_status=$child_status
    fi
done
if (( first_status != 0 )); then
    echo "ERROR: one or more browser sessions failed to open" >&2
    exit "$first_status"
fi

# Extract from each
agent-browser --session site1 get text body > site1.txt
agent-browser --session site2 get text body > site2.txt
agent-browser --session site3 get text body > site3.txt
```

### A/B Testing Sessions

```bash
# Test different user experiences
agent-browser --session variant-a open "https://app.com?variant=a"
agent-browser --session variant-b open "https://app.com?variant=b"

# Compare
agent-browser --session variant-a screenshot "${XDG_STATE_HOME:-$HOME/.local/state}/agent-browser/variant-a.png"
agent-browser --session variant-b screenshot "${XDG_STATE_HOME:-$HOME/.local/state}/agent-browser/variant-b.png"
```

## Default Session

When `--session` is omitted, commands use the default session:

```bash
# These use the same default session
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser close  # Closes default session
```

## Session Cleanup

```bash
# Close specific session
agent-browser --session auth close

# List active sessions
agent-browser session list
```

## Best Practices

### 1. Name Sessions Semantically

```bash
# GOOD: Clear purpose
agent-browser --session github-auth open https://github.com
agent-browser --session docs-scrape open https://docs.example.com

# AVOID: Generic names
agent-browser --session s1 open https://github.com
```

### 2. Always Clean Up

```bash
# Close sessions when done
agent-browser --session auth close
agent-browser --session scrape close
```

### 3. Handle State Files Securely

```bash
# Don't commit state files (contain auth tokens!)
echo "*.auth-state.json" >> .gitignore

# Delete after use
mv "$STATE_FILE" "$STATE_FILE.bak"
```

### 4. Timeout Long Sessions

```bash
# Set timeout for automated scripts
timeout 60 agent-browser --session long-task get text body
```
