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

ERRORS=()

run_validator() {
    local label=$1
    local executable=$2
    shift 2

    if ! command -v "$executable" >/dev/null 2>&1; then
        ERRORS+=("${label}: ${executable} is unavailable")
        return
    fi

    local output
    local status
    if output=$("$@" 2>&1); then
        return
    else
        status=$?
    fi
    ERRORS+=("${label} failed (exit ${status}):"$'\n'"${output}")
}

# ── FLEXT: ruff check on single file ──
if [[ "$PROJECT" == "flext" ]]; then
    run_validator "ruff check on ${FILE}" ruff ruff check "$FILE"
fi

# ── MCB: cargo check on modified crate ──
if [[ "$PROJECT" == "mcb" ]]; then
    if [[ "$FILE" == *.rs ]]; then
        run_validator \
            "cargo check for ${FILE}" \
            cargo \
            cargo check --message-format=short
    fi
fi

# ── cosmos-main: yamllint on YAML files ──
if [[ "$PROJECT" == "cosmos-main" ]]; then
    if [[ "$FILE" == *.yml || "$FILE" == *.yaml ]]; then
        run_validator \
            "yamllint on ${FILE}" \
            yamllint \
            yamllint -d relaxed "$FILE"
    fi
fi

if (( ${#ERRORS[@]} > 0 )); then
    reason=$(printf '%s\n\n' "${ERRORS[@]}")
    jq -nc --arg reason "$reason" '{"decision":"block","reason":$reason}'
fi

exit 0
