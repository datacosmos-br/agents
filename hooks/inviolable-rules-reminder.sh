#!/usr/bin/env bash
# UserPromptSubmit hook: re-inject the operator's inviolable rules digest.
# Why: vendor-confirmed rule decay — instructions loaded once at session start
# lose influence as context fills; deterministic re-injection preserves them.
# SSOT: ~/.claude/AGENTS.md §0/§0.1 (LEI SUPREMA + Mandamentos I–VI).
set -euo pipefail

cat >/dev/null

DIGEST='⛔ LEI SUPREMA: resolver na RAIZ, nunca esconder/bypass/fallback; verde só com verificação. Mandamentos I–VI (~/.claude/AGENTS.md §0.1): I honestidade 100% (evidência=alegação); II não sabe→pesquise antes; III strict sempre; IV bypass encontrado→desfazer ou perguntar NA HORA; V executar o pedido do operador — perigoso/contra-regras→expor conflito e pedir decisão (nunca recusar em silêncio, nunca às cegas); VI YAGNI/KISS/SOLID/DI em tudo.'

jq -nc --arg ctx "$DIGEST" \
  '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":$ctx}}'
exit 0
