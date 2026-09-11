#!/usr/bin/env bash
set -euo pipefail

# wip-beads.sh — batch Bead governance processor (CSV-driven, wip-hier style)
# Default: dry-run report. --apply writes (bd note/update/label/link/parent).
# CSV columns: id,title,status,issue_type,priority,parent_id,labels,dep_count

readonly PROG="${0##*/}"
readonly START_TS="$(date -Iseconds)"
readonly LOGDIR="${XDG_STATE_HOME:-${HOME}/.local/state}/wip-beads"
readonly CSV_DEFAULT="./wip-beads-open.csv"

die() { printf 'erro: %s\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }
have bd || die "bd nao encontrado no PATH"
have jq || die "jq nao encontrado no PATH"
mkdir -p "$LOGDIR"

usage() {
  cat <<EOF
${PROG} — batch bead governance processor

  ${PROG} [--csv <file>] [--beads <id1,id2,...>] [--limits <n>] [--mode <plan>] [--apply] [--map <file>] [--dry-run] [--json-report <file>]

Modes (--mode):
  collect     coleta evidencia de workspace e anota beads (WORKSPACE SYNC)
  classify    classifica bugfix/hotfix/feature sem epic; tasks -> epics poucos
  align       re-parent para epics canonicos; valida alinhamento
  unblock     calcula cadeia de dependencias + sugere destravamento
  title       melhora titulos/tags de forma padronizada
  deferred    ajusta status de beads deferred
  all         executa todos os modos em ciclo

Paths:
  --csv           CSV de entrada (default: ${CSV_DEFAULT})
  --beads         lista separada por virgula de IDs (default: todos do CSV)
  --limits        limite de beads por lote (default: 25)
  --apply         executa mutacoes (bd write); default = dry-run
  --map           CSV de mapping para align (colunas: bead_id,desired_parent)
  --dry-run       explicita dry-run (default)
  --json-report   escreve resumo JSON de cada modo (counts por acao)

Logs: ${LOGDIR}/<ts>-log e ${LOGDIR}/latest.log
EOF
}

CSV_FILE="$CSV_DEFAULT"
MODE="collect"
APPLY=0
LIMITS=25
BEADS=""
MAP_FILE=""
DRY_RUN=1
JSON_REPORT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --csv) CSV_FILE="$2"; shift 2 ;;
    --beads) BEADS="$2"; shift 2 ;;
    --limits) LIMITS="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --apply) APPLY=1; DRY_RUN=0; shift ;;
    --map) MAP_FILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; APPLY=0; shift ;;
    --json-report) JSON_REPORT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "flag desconhecida: $1" ;;
  esac
done

MODE="${MODE:-collect}"
LOG="${LOGDIR}/${START_TS}-${PPID}-${MODE}.log"
exec > >(tee "$LOG") 2>&1
ln -sf "$(basename "$LOG")" "$LOGDIR/latest.log"

# ---------------------------------------------------------------
# Parse CSV
# ---------------------------------------------------------------
BEAD_IDS=()
declare -A CSV_STATUS
declare -A CSV_PARENT
declare -A CSV_ISSUE_TYPE
declare -A CSV_TITLE
declare -A CSV_LABELS

if [[ -n "$BEADS" ]]; then
  IFS=',' read -ra BEAD_IDS <<< "$BEADS"
elif [[ -f "$CSV_FILE" ]]; then
  # Skip header, parse CSV with proper quoting handling
  tail -n +2 "$CSV_FILE" | while IFS=',' read -r id title status issue_type priority parent_id labels dep_count; do
    # Remove surrounding quotes if present
    id="${id//\"/}"
    printf '%s\n' "$id"
  done > /tmp/wip-beads-ids.$$
  BEAD_IDS=($(cat /tmp/wip-beads-ids.$$))
  rm -f /tmp/wip-beads-ids.$$

  # Also populate lookup arrays from CSV for collect mode comparison
  while IFS=',' read -r id title status issue_type priority parent_id labels dep_count; do
    id="${id//\"/}"
    title="${title//\"/}"
    status="${status//\"/}"
    issue_type="${issue_type//\"/}"
    parent_id="${parent_id//\"/}"
    labels="${labels//\"/}"
    CSV_STATUS["$id"]="$status"
    CSV_PARENT["$id"]="$parent_id"
    CSV_ISSUE_TYPE["$id"]="$issue_type"
    CSV_TITLE["$id"]="$title"
    CSV_LABELS["$id"]="$labels"
  done < <(tail -n +2 "$CSV_FILE")
fi

total=${#BEAD_IDS[@]}
printf 'MODE=%s APPLY=%s DRY_RUN=%s total=%d limits=%d\n' "$MODE" "$APPLY" "$DRY_RUN" "$total" "$LIMITS"

# JSON report accumulator
declare -A REPORT_COUNTS
REPORT_COUNTS[processed]=0
REPORT_COUNTS[mutated]=0
REPORT_COUNTS[errors]=0
REPORT_COUNTS[skipped]=0

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
log_cmd() {
  local cmd="$1"
  local id="$2"
  local mode="$3"
  printf '  [CMD %s] %s\n' "$mode" "$cmd" >> "$LOG"
}

mutate() {
  local id="$1"
  local mode="$2"
  local cmd="$3"
  if [[ $APPLY -eq 1 ]]; then
    log_cmd "$cmd" "$id" "$mode"
    if eval "$cmd" >> "$LOG" 2>&1; then
      ((REPORT_COUNTS[mutated]+=1)) || true
      printf '  [APPLIED %s] %s\n' "$mode" "$id"
    else
      ((REPORT_COUNTS[errors]+=1)) || true
      printf '  [ERROR %s] %s: comando falhou\n' "$mode" "$id"
    fi
  else
    printf '  [DRY-RUN %s] %s: %s\n' "$mode" "$id" "$cmd"
  fi
  ((REPORT_COUNTS[processed]+=1)) || true
}

report_skip() {
  local mode="$1"
  local id="$2"
  local reason="$3"
  printf '  [SKIP %s] %s: %s\n' "$mode" "$id" "$reason"
  ((REPORT_COUNTS[skipped]+=1)) || true
}

write_json_report() {
  [[ -z "$JSON_REPORT" ]] && return
  local mode="$1"
  local -n counts=$2
  jq -n \
    --arg mode "$mode" \
    --arg timestamp "$(date -Iseconds)" \
    --argjson processed "${counts[processed]}" \
    --argjson mutated "${counts[mutated]}" \
    --argjson errors "${counts[errors]}" \
    --argjson skipped "${counts[skipped]}" \
    '{mode: $mode, timestamp: $timestamp, processed: $processed, mutated: $mutated, errors: $errors, skipped: $skipped}' >> "$JSON_REPORT"
}

reset_counts() {
  REPORT_COUNTS[processed]=0
  REPORT_COUNTS[mutated]=0
  REPORT_COUNTS[errors]=0
  REPORT_COUNTS[skipped]=0
}

declare -A BEAD_JSON_CACHE

load_bead_json_cache() {
  local snapshot id encoded bead_json
  BEAD_JSON_CACHE=()
  snapshot="$(bd list --all --flat --json)"
  while IFS=$'\t' read -r id encoded; do
    [[ -n "$id" ]] || continue
    bead_json="$(printf '%s' "$encoded" | base64 --decode)"
    BEAD_JSON_CACHE["$id"]="$bead_json"
  done < <(jq -r '.[] | [.id, (. | @base64)] | @tsv' <<< "$snapshot")
}

get_bead_json() {
  local id="$1"
  if [[ -z "${BEAD_JSON_CACHE[$id]:-}" ]]; then
    BEAD_JSON_CACHE[$id]="$(bd show "$id" --json 2>/dev/null | jq -c '.[0] // empty')"
  fi
  printf '%s' "${BEAD_JSON_CACHE[$id]}"
}

get_bead_field() {
  local id="$1"
  local field="$2"
  get_bead_json "$id" | jq -r ".$field // empty"
}

# ---------------------------------------------------------------
# Mode: collect
# ---------------------------------------------------------------
mode_collect() {
  local id="$1"
  local note_ts="$(date -Iseconds)"
  local note="WORKSPACE SYNC ${note_ts} (wip-beads.sh collect): root develop+submods+worktrees evidencia coletada; verifica alignment/epics/status no CSV ${CSV_FILE}."

  # Get current status and parent from bd
  local curr_status curr_parent
  curr_status=$(get_bead_field "$id" "status")
  curr_parent=$(get_bead_field "$id" "parent")

  local csv_status="${CSV_STATUS[$id]:-}"
  local csv_parent="${CSV_PARENT[$id]:-}"

  local changed=0
  [[ "$curr_status" != "$csv_status" ]] && changed=1
  [[ "$curr_parent" != "$csv_parent" ]] && changed=1

  if [[ $changed -eq 1 ]]; then
    local cmd="bd note \"$id\" \"$note\""
    mutate "$id" "collect" "$cmd"
  else
    report_skip "collect" "$id" "status/parent inalterados (bd=$curr_status/$curr_parent, csv=$csv_status/$csv_parent)"
  fi
}

# ---------------------------------------------------------------
# Mode: classify
# ---------------------------------------------------------------
mode_classify() {
  local id="$1"
  local issue_type
  issue_type=$(get_bead_field "$id" "issue_type")
  local parent_now
  parent_now=$(get_bead_field "$id" "parent")

  case "$issue_type" in
    bug|bugfix|hotfix)
      if [[ -n "$parent_now" ]]; then
        printf '  [classify] %s: %s com parent=%s -> remover parent\n' "$id" "$issue_type" "$parent_now"
        local cmd="bd update \"$id\" --parent \"\""
        mutate "$id" "classify" "$cmd"
      else
        report_skip "classify" "$id" "bug/hotfix sem parent OK"
      fi
      ;;
    feature|task|chore|decision|epic|convoy|gate|rig)
      if [[ -z "$parent_now" && "$issue_type" != "epic" ]]; then
        printf '  [classify] %s: %s sem parent (epic esperado)\n' "$id" "$issue_type"
      else
        report_skip "classify" "$id" "$issue_type parent OK ($parent_now)"
      fi
      ;;
    *)
      report_skip "classify" "$id" "tipo desconhecido: $issue_type"
      ;;
  esac
}

# ---------------------------------------------------------------
# Mode: align
# ---------------------------------------------------------------
declare -A ALIGN_MAP

load_align_map() {
  [[ -z "$MAP_FILE" || ! -f "$MAP_FILE" ]] && return
  while IFS=',' read -r bead_id desired_parent; do
    bead_id="${bead_id//\"/}"
    desired_parent="${desired_parent//\"/}"
    [[ -n "$bead_id" ]] && ALIGN_MAP["$bead_id"]="$desired_parent"
  done < <(tail -n +2 "$MAP_FILE")
}

mode_align() {
  local id="$1"
  local issue_type
  issue_type=$(get_bead_field "$id" "issue_type")
  local curr_parent
  curr_parent=$(get_bead_field "$id" "parent")

  local desired_parent="${ALIGN_MAP[$id]:-}"

  if [[ -n "$desired_parent" ]]; then
    if [[ "$curr_parent" != "$desired_parent" ]]; then
      printf '  [align] %s: parent atual=%s desejado=%s\n' "$id" "${curr_parent:-vazio}" "$desired_parent"
      local cmd="bd update \"$id\" --parent \"$desired_parent\""
      mutate "$id" "align" "$cmd"
    else
      report_skip "align" "$id" "parent ja alinhado ($curr_parent)"
    fi
  elif [[ "$issue_type" != "epic" && -z "$curr_parent" ]]; then
    printf '  [align] %s: %s sem parent (map nao fornecido)\n' "$id" "$issue_type"
    report_skip "align" "$id" "sem map para definir parent desejado"
  else
    report_skip "align" "$id" "OK (parent=$curr_parent)"
  fi
}

# ---------------------------------------------------------------
# Mode: unblock
# ---------------------------------------------------------------
mode_unblock() {
  local id="$1"
  local status
  status=$(get_bead_field "$id" "status")

  if [[ "$status" != "blocked" ]]; then
    report_skip "unblock" "$id" "status=$status (nao blocked)"
    return
  fi

  # Get blockers (dependencies where this bead depends on others)
  local deps_json
  deps_json=$(bd dep list "$id" --json 2>/dev/null)
  local blocker_count
  blocker_count=$(echo "$deps_json" | jq 'length')

  if [[ "$blocker_count" -eq 0 ]]; then
    printf '  [unblock] %s: blocked mas sem dependencias registradas\n' "$id"
    return
  fi

  local unblockable=0
  local blocked_by_open=0

  echo "$deps_json" | jq -c '.[]' | while read -r dep; do
    local blocker_id blocker_status
    blocker_id=$(echo "$dep" | jq -r '.id // empty')
    blocker_status=$(echo "$dep" | jq -r '.status // empty')

    if [[ "$blocker_status" == "closed" || "$blocker_status" == "done" || "$blocker_status" == "completed" ]]; then
      printf '  [unblock] %s: blocker %s esta %s (destravavel)\n' "$id" "$blocker_id" "$blocker_status"
      ((unblockable+=1)) || true
    else
      printf '  [unblock] %s: blocker %s esta %s (aberto)\n' "$id" "$blocker_id" "$blocker_status"
      ((blocked_by_open+=1)) || true
    fi
  done

  if [[ $unblockable -gt 0 && $blocked_by_open -eq 0 ]]; then
    printf '  [unblock] %s: TODOS blockers fechados -> pode desbloquear\n' "$id"
  elif [[ $unblockable -gt 0 ]]; then
    printf '  [unblock] %s: %d/%d blockers fechados, %d abertos\n' "$id" "$unblockable" "$blocker_count" "$blocked_by_open"
  else
    printf '  [unblock] %s: nenhum blocker fechado (%d abertos)\n' "$id" "$blocked_by_open"
  fi

  ((REPORT_COUNTS[processed]+=1)) || true
}

# ---------------------------------------------------------------
# Mode: title
# ---------------------------------------------------------------
normalize_title() {
  local title="$1"
  # Preserve existing [scope] prefix
  local scope_prefix=""
  if [[ "$title" =~ ^\[([^]]+)\]\ (.*)$ ]]; then
    scope_prefix="[${BASH_REMATCH[1]}] "
    title="${BASH_REMATCH[2]}"
  fi
  # Remove WIP/wip prefixes (case insensitive, with or without brackets/parens)
  title="${title#[Ww][Ii][Pp][[:space:]]*}"
  title="${title#\[[Ww][Ii][Pp]\][[:space:]]*}"
  title="${title#\([Ww][Ii][Pp]\)[[:space:]]*}"
  # Collapse multiple spaces
  title="$(echo "$title" | sed 's/[[:space:]]\+/ /g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  echo "${scope_prefix}${title}"
}

normalize_labels() {
  local labels="$1"
  # ponytail: preserve label case (priority:P0 e convenção do projeto); só trim+dedup
  echo "$labels" | tr ';' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | awk '!seen[$0]++' | paste -sd ';' -
}

mode_title() {
  local id="$1"
  local curr_title curr_labels
  curr_title=$(get_bead_field "$id" "title")
  curr_labels=$(get_bead_field "$id" "labels" | jq -r 'join(";")')

  local new_title new_labels
  new_title=$(normalize_title "$curr_title")
  new_labels=$(normalize_labels "$curr_labels")

  if [[ "$curr_title" != "$new_title" || "$curr_labels" != "$new_labels" ]]; then
    printf '  [title] %s: titulo alterado\n' "$id"
    printf '    OLD: %s\n' "$curr_title"
    printf '    NEW: %s\n' "$new_title"
    if [[ "$curr_labels" != "$new_labels" ]]; then
      printf '    LABELS: %s -> %s\n' "$curr_labels" "$new_labels"
    fi
    local cmd="bd update \"$id\" --title \"$new_title\""
    if [[ "$curr_labels" != "$new_labels" ]]; then
      # Build label args
      local label_args=""
      IFS=';' read -ra lbls <<< "$new_labels"
      for lbl in "${lbls[@]}"; do
        [[ -n "$lbl" ]] && label_args="$label_args --add-label \"$lbl\""
      done
      cmd="$cmd $label_args"
    fi
    mutate "$id" "title" "$cmd"
  else
    report_skip "title" "$id" "ja padronizado"
  fi
}

# ---------------------------------------------------------------
# Mode: deferred
# ---------------------------------------------------------------
mode_deferred() {
  local id="$1"
  local status
  status=$(get_bead_field "$id" "status")

  if [[ "$status" != "deferred" ]]; then
    report_skip "deferred" "$id" "status=$status (nao deferred)"
    return
  fi

  local assignee
  assignee=$(get_bead_field "$id" "owner")

  local note="REVALIDACAO DEFERRED $(date -Iseconds) (wip-beads.sh deferred): bead com status deferred reavaliado. Assignee: ${assignee:-sem assignee}. Verificar se deve retornar a open ou permanecer deferred."

  printf '  [deferred] %s: status=deferred, assignee=%s\n' "$id" "${assignee:-vazio}"
  local cmd="bd note \"$id\" \"$note\""
  mutate "$id" "deferred" "$cmd"
}

# ---------------------------------------------------------------
# Main batch loop
# ---------------------------------------------------------------
load_align_map

# For 'all' mode, run each mode sequentially
MODES_TO_RUN=()
if [[ "$MODE" == "all" ]]; then
  MODES_TO_RUN=(collect classify align unblock title deferred)
else
  MODES_TO_RUN=("$MODE")
fi

for run_mode in "${MODES_TO_RUN[@]}"; do
  load_bead_json_cache
  printf '\n=== MODO: %s ===\n' "$run_mode"
  reset_counts

  batch=0
  for (( i=0; i<total; i+=LIMITS )); do
    batch=$((batch+1))
    slice=("${BEAD_IDS[@]:i:LIMITS}")
    printf '\n--- BATCH %d (%d beads) ---\n' "$batch" "${#slice[@]}"
    for id in "${slice[@]}"; do
      case "$run_mode" in
        collect) mode_collect "$id" ;;
        classify) mode_classify "$id" ;;
        align) mode_align "$id" ;;
        unblock) mode_unblock "$id" ;;
        title) mode_title "$id" ;;
        deferred) mode_deferred "$id" ;;
      esac
    done
  done

  printf '\n--- RESUMO %s: processed=%d mutated=%d errors=%d skipped=%d ---\n' \
    "$run_mode" "${REPORT_COUNTS[processed]}" "${REPORT_COUNTS[mutated]}" "${REPORT_COUNTS[errors]}" "${REPORT_COUNTS[skipped]}"
  write_json_report "$run_mode" REPORT_COUNTS
done

printf '\n%s: %d beads, %d batches. logs=%s\n' "$PROG" "$total" "$batch" "$LOG"