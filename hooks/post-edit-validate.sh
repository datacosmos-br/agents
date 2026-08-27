#!/usr/bin/env bash
# Post-edit hook: validate modified files after Write/Edit
# Runs project-specific quick checks on the modified file only
set -euo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

[[ "$TOOL" != "Write" && "$TOOL" != "Edit" ]] && exit 0

FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[[ -z "$FILE" || ! -f "$FILE" ]] && exit 0

# Detect project type
PROJECT=""
if [[ -f "pyproject.toml" ]] && [[ -d "flext-core" || -d "flext-infra" ]]; then
    PROJECT="flext"
elif [[ -f "Cargo.toml" ]] && [[ -d "mcb-domain" || -d "src" ]]; then
    PROJECT="mcb"
elif [[ -d "apps" && -d "makefiles" && -f "Makefile" ]]; then
    PROJECT="cosmos-main"
fi

[[ -z "$PROJECT" ]] && exit 0

ERRORS=""

# ── FLEXT: ruff check on single file ──
if [[ "$PROJECT" == "flext" ]]; then
    if command -v ruff &>/dev/null; then
        if ! ruff check "$FILE" 2>&1; then
            ERRORS="ruff check failed on $FILE"
        fi
    fi
fi

# ── MCB: cargo check on modified crate ──
if [[ "$PROJECT" == "mcb" ]]; then
    if [[ "$FILE" == *.rs ]]; then
        # Try cargo check on the workspace (fast for single-file changes)
        if command -v cargo &>/dev/null; then
            CARGO_OUT=$(cargo check --message-format=short 2>&1) || true
            if echo "$CARGO_OUT" | grep -q "error"; then
                ERRORS="cargo check found errors"
            fi
        fi
    fi
fi

# ── cosmos-main: yamllint on YAML files ──
if [[ "$PROJECT" == "cosmos-main" ]]; then
    if [[ "$FILE" == *.yml || "$FILE" == *.yaml ]]; then
        if command -v yamllint &>/dev/null; then
            if ! yamllint -d relaxed "$FILE" 2>&1; then
                ERRORS="yamllint failed on $FILE"
            fi
        fi
    fi
fi

if [[ -n "$ERRORS" ]]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "additionalContext": "⚠️ Validation failed for $FILE:\n$ERRORS\n\nFix before continuing."
  }
}
EOF
fi

exit 0
