#!/usr/bin/env bash
# Generic SessionStart hook: local repository facts only.
set -euo pipefail

cat >/dev/null
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

branch=$(git branch --show-current 2>/dev/null || true)
root=$(git rev-parse --show-toplevel)
if git status --porcelain=v1 --untracked-files=normal | grep -q .; then
    state=dirty
else
    state=clean
fi
context="[git] root=${root} branch=${branch:-detached} state=${state}"
jq -nc --arg context "$context" \
    '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$context}}'
