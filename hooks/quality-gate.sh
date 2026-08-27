#!/usr/bin/env bash
# Generic Stop hook: expose unlanded repository state without cross-repo calls.
set -euo pipefail

input=$(cat)
active=$(jq -r '.stop_hook_active // false' <<<"$input")
[[ "$active" == true ]] && exit 0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
dirty=$(git status --porcelain=v1 --untracked-files=normal)
[[ -z "$dirty" ]] && exit 0

count=$(wc -l <<<"$dirty" | tr -d ' ')
reason="Unlanded repository state: ${count} path(s). A phase is not DONE until its approved PR is merged into the configured integration branch and its Bead is closed with evidence."
jq -nc --arg reason "$reason" '{"decision":"block","reason":$reason}'
