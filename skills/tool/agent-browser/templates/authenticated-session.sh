#!/bin/bash
# Template: Authenticated Session Workflow
# Login once, save state, reuse for subsequent runs
#
# Usage:
#   ./authenticated-session.sh <login-url> [state-file] [expected-auth-url-prefix]
#
# Setup:
#   1. Run once to see your form structure
#   2. Note the @refs for your fields
#   3. Uncomment LOGIN FLOW section and update refs

set -euo pipefail

LOGIN_URL="${1:?Usage: $0 <login-url> [state-file] [expected-auth-url-prefix]}"
STATE_FILE="${2:-./auth-state.json}"
EXPECTED_AUTH_URL_PREFIX="${3:-}"

echo "Authentication workflow for: $LOGIN_URL"

# ══════════════════════════════════════════════════════════════
# SAVED STATE: Skip login if we have valid saved state
# ══════════════════════════════════════════════════════════════
if [[ -f "$STATE_FILE" ]]; then
    : "${EXPECTED_AUTH_URL_PREFIX:?Expected authenticated URL prefix is required when restoring state}"
    echo "Loading saved authentication state..."
    agent-browser state load "$STATE_FILE"
    agent-browser open "$EXPECTED_AUTH_URL_PREFIX"
    agent-browser wait --load networkidle

    CURRENT_URL=$(agent-browser get url)
    if [[ "$CURRENT_URL" == "$EXPECTED_AUTH_URL_PREFIX"* ]]; then
        echo "Session restored successfully!"
        agent-browser snapshot -i
        exit 0
    fi
    echo "ERROR: restored state did not reach the expected authenticated URL" >&2
    agent-browser close
    exit 1
fi

# ══════════════════════════════════════════════════════════════
# DISCOVERY MODE: Show form structure (remove after setup)
# ══════════════════════════════════════════════════════════════
echo "Opening login page..."
agent-browser open "$LOGIN_URL"
agent-browser wait --load networkidle

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ LOGIN FORM STRUCTURE                                    │"
echo "├─────────────────────────────────────────────────────────┤"
agent-browser snapshot -i
echo "└─────────────────────────────────────────────────────────┘"
echo ""
echo "Next steps:"
echo "  1. Note refs: @e? = username, @e? = password, @e? = submit"
echo "  2. Uncomment LOGIN FLOW section below"
echo "  3. Replace @e1, @e2, @e3 with your refs"
echo "  4. Delete this DISCOVERY MODE section"
echo "Authentication was not executed; discovery is not a successful login."
echo ""
agent-browser close
exit 2

# ══════════════════════════════════════════════════════════════
# LOGIN FLOW: Uncomment and customize after discovery
# ══════════════════════════════════════════════════════════════
# : "${APP_USERNAME:?Set APP_USERNAME environment variable}"
# : "${APP_PASSWORD:?Set APP_PASSWORD environment variable}"
#
# agent-browser open "$LOGIN_URL"
# agent-browser wait --load networkidle
# agent-browser snapshot -i
#
# # Fill credentials (update refs to match your form)
# agent-browser fill @e1 "$APP_USERNAME"
# agent-browser fill @e2 "$APP_PASSWORD"
# agent-browser click @e3
# agent-browser wait --load networkidle
#
# # Verify login succeeded
# : "${EXPECTED_AUTH_URL_PREFIX:?Expected authenticated URL prefix is required before running login}"
# FINAL_URL=$(agent-browser get url)
# if [[ "$FINAL_URL" != "$EXPECTED_AUTH_URL_PREFIX"* ]]; then
#     echo "ERROR: login did not reach the expected authenticated URL" >&2
#     agent-browser screenshot "${XDG_STATE_HOME:-$HOME/.local/state}/agent-browser/login-failed.png"
#     agent-browser close
#     exit 1
# fi
#
# # Save state for future runs
# echo "Saving authentication state to: $STATE_FILE"
# agent-browser state save "$STATE_FILE"
# echo "Login successful!"
# agent-browser snapshot -i
