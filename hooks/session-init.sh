#!/usr/bin/env bash
# Generic SessionStart hook: local repository facts only.
set -euo pipefail

cat >/dev/null
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

if branch=$(git symbolic-ref --quiet --short HEAD); then
    :
else
    branch_status=$?
    if [[ "$branch_status" -eq 1 ]]; then
        branch=detached
    else
        exit "$branch_status"
    fi
fi
root=$(git rev-parse --show-toplevel)
dirty=$(git status --porcelain=v1 --untracked-files=normal)
if [[ -n "$dirty" ]]; then
    state=dirty
else
    state=clean
fi
context="[git] root=${root} branch=${branch} state=${state}"
jq -nc --arg context "$context" \
    '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$context}}'
