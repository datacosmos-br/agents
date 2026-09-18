#!/usr/bin/env bash
set -euo pipefail

readonly PROG="${0##*/}"

usage() {
  cat <<EOF
Usage: ${PROG} --limit N --integration REF [--output FILE | --dry-run]
       [--offset N] [--beads ID[,ID...]]... [--all]

Export a bounded Beads reconciliation queue as CSV without mutating Beads.
--beads may be repeated and each value may contain comma-separated IDs.
--dry-run writes CSV to stdout and creates no output file. Closed beads are
excluded unless --all is set. Use --limit 0 only for an explicit full inventory.
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

append_beads() {
  local value="$1"
  local bead
  local -a values=()

  IFS=',' read -r -a values <<<"$value"
  ((${#values[@]} > 0)) || die "--beads requires at least one ID"
  for bead in "${values[@]}"; do
    [[ -n "$bead" && "$bead" != *[[:space:]]* ]] ||
      die "--beads IDs must be non-empty and contain no whitespace"
    bead_ids+=("$bead")
  done
}

limit=""
offset=0
output=""
integration=""
include_closed=0
dry_run=0
declare -a bead_ids=()

while (($# > 0)); do
  case "$1" in
    --limit)
      (($# >= 2)) || die "--limit requires a value"
      limit="$2"
      shift 2
      ;;
    --offset)
      (($# >= 2)) || die "--offset requires a value"
      offset="$2"
      shift 2
      ;;
    --beads)
      (($# >= 2)) || die "--beads requires one or more IDs"
      append_beads "$2"
      shift 2
      ;;
    --integration)
      (($# >= 2)) || die "--integration requires a Git ref"
      integration="$2"
      shift 2
      ;;
    --output)
      (($# >= 2)) || die "--output requires a path"
      output="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --all)
      include_closed=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ "$limit" =~ ^[0-9]+$ ]] || die "--limit is required and must be a non-negative integer"
[[ "$offset" =~ ^[0-9]+$ ]] || die "--offset must be a non-negative integer"
[[ -n "$integration" ]] || die "--integration is required"
if ((dry_run)); then
  [[ -z "$output" ]] || die "--dry-run and --output are mutually exclusive"
else
  [[ -n "$output" ]] || die "--output is required unless --dry-run is used"
fi
command -v bd >/dev/null || die "bd not found"
command -v git >/dev/null || die "git not found"
command -v jq >/dev/null || die "jq not found"

repo_root="$(git rev-parse --show-toplevel)"
integration_sha="$(git rev-parse --verify "${integration}^{commit}")"
worktree_evidence="$({ git worktree list --porcelain; printf '\n'; } | jq -Rrs '
  split("\n\n")
  | map(select(length > 0) | split("\n") | map(select(length > 0)) | join(" "))
  | join(" | ")
')"

beads=""
if ((${#bead_ids[@]} > 0)); then
  printf -v beads '%s\n' "${bead_ids[@]}"
  beads="${beads%$'\n'}"
fi

render_csv() {
  bd list --all --limit 0 --flat --json |
    jq -r \
      --arg beads "$beads" \
      --arg repo_root "$repo_root" \
      --arg integration "$integration" \
      --arg integration_sha "$integration_sha" \
      --arg worktrees "$worktree_evidence" \
      --argjson include_closed "$include_closed" \
      --argjson limit "$limit" \
      --argjson offset "$offset" '
      def requested_ids:
        if ($beads | length) == 0 then [] else ($beads | split("\n") | unique) end;
      def selected($requested):
        .id as $id
        | ($requested | length) == 0 or ($requested | index($id)) != null;
      def weak_title:
        (.title | ascii_downcase | test("^(wip|fix|fixes|todo|test|update|changes|misc)([: ]|$)"));
      def weak_description: ((.description // "") | length) < 40;
      def has_label($name): ((.labels // []) | index($name)) != null;
      def review_flags($statuses):
        [
          if .status == "in_progress" then "verify-claim-evidence" else empty end,
          if .status == "deferred" then "verify-deferred-evidence" else empty end,
          if .status != "deferred" and has_label("state:deferred-backlog") then "deferred-status-mismatch" else empty end,
          if .issue_type == "bug" and .parent != null then "parented-bug" else empty end,
          if .issue_type == "bug" and (has_label("bugfix") | not) then "missing-bugfix" else empty end,
          if has_label("bugfix") and .issue_type != "bug" then "bugfix-on-nonbug" else empty end,
          if has_label("hotfix") and (.issue_type != "bug" or .priority == null or .priority > 1) then "invalid-hotfix" else empty end,
          if .parent != null and $statuses[.parent] == "closed" then "closed-parent" else empty end,
          if weak_title then "weak-title" else empty end,
          if weak_description then "weak-description" else empty end
        ] | join(";");
      if type == "array" then . else error("bd list JSON must be an array") end
      | . as $all
      | requested_ids as $requested
      | ($all | map(.id)) as $available
      | ($requested - $available) as $missing
      | if ($missing | length) > 0 then error("unknown bead IDs: \($missing | join(","))") else . end
      | ($all | map({key: .id, value: .status}) | from_entries) as $statuses
      | ["id", "revision", "status", "priority", "type", "title", "parent", "assignee", "defer_until", "labels", "review_flags", "description", "repository", "integration_ref", "integration_sha", "worktrees"],
        ($all
          | map(select(selected($requested) and ($include_closed == 1 or .status != "closed")))
          | sort_by(.id)
          | .[$offset:(if $limit == 0 then length else ($offset + $limit) end)][]
          | [
              .id,
              (.revision // ""),
              .status,
              .priority,
              .issue_type,
              .title,
              (.parent // ""),
              (.assignee // ""),
              (.defer_until // ""),
              ((.labels // []) | join(";")),
              review_flags($statuses),
              (.description // ""),
              $repo_root,
              $integration,
              $integration_sha,
              $worktrees
            ])
      | @csv
      '
}

if ((dry_run)); then
  printf 'mode=dry-run limit=%s offset=%s beads=%s integration=%s\n' \
    "$limit" "$offset" "${beads//$'\n'/,}" "$integration" >&2
  render_csv
  exit 0
fi

if [[ "$output" == */* ]]; then
  output_dir="${output%/*}"
  [[ -n "$output_dir" ]] || output_dir="/"
else
  output_dir="."
fi
output_name="${output##*/}"
[[ -d "$output_dir" && ! -L "$output_dir" ]] ||
  die "output parent must be an existing physical directory: $output_dir"
[[ -n "$output_name" && ! -d "$output" && ! -L "$output" ]] ||
  die "output must be a file path and must not be a symlink: $output"

tmp="$(mktemp "${output_dir}/.${output_name}.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
render_csv >"$tmp"
mv -- "$tmp" "$output"
trap - EXIT

printf 'mode=read-only output=%s limit=%s offset=%s beads=%s integration=%s sha=%s\n' \
  "$output" "$limit" "$offset" "${beads//$'\n'/,}" "$integration" "$integration_sha"
