# HANDOFF — Governance Runtime Program (ag-zrh) · 2026-09-11

> Use com `bd prime` no checkout `~/agents` e leia este arquivo antes da primeira ação.
> Plano canônico: `docs/plans/20260910-governance-runtime-program.md` (fonte única de sequência/DoD).

## 1. Prompt de reinício (colar numa sessão nova)

```text
Handoff: Governance Runtime Program (bead épico ag-zrh).
1. Rode bd prime (env -u BEADS_DOLT_SERVER_DATABASE) e leia
   docs/plans/20260911-handoff-governance-runtime-program.md (referência)
   e docs/plans/20260910-governance-runtime-program.md (plano canônico com DoD).
2. Remonte o TODO a partir da tabela de status do plano + bd list --status open —
   nunca de memória. Cada item carrega bead-ID e linha do plano.
3. Estado: worktree ~/ai-hub-wt/green-baseline (branch fix/green-baseline @ d590d1cfb)
   com grind verde 2564→2467 por classe (namespace 1100, codemod 1033, pyrefly 146,
   pyright 40, lint 42, silent-failure 40, mypy 16, duplication 36).
4. PRIMEIRO passo material: ag-nq7q — `ai-hub ai-hub-sync-crg-workspaces`
   (CRG RED: drift de 10+ workspaces) até `--check` exit 0.
5. Depois, PASO 1 do plano: em fix/green-baseline, `git fetch && git merge --no-ff
   origin/dev` (dev do ai-hub já tem 0.5.0 do ator paralelo) e re-medir.
6. PROPOSTA aguarda aprovação do operador (seção PROPOSTA do plano; beads
   ag-q4w1 esteira, ag-m9lu piloto). Sem aprovação, o grind por classe continua
   usando só make fix/mod/check/test + make gen ×2.
7. Disciplina permanente: toda correção usa worktree dedicada (nunca checkout
   compartilhado), roda gates após cada onda ({make fix → test → check}),
   docs/beads/plano atualizados no mesmo passo, evidência de 4 fontes para
   qualquer fechamento, push pendente do plano dev agents (aguardar WIP do ator
   AGENTS.md/CLAUDE.md liberar, depois git pull --rebase && push).
```

## 2. Como as conclusões foram remontadas (triângulo de verificação)

Todo fechamento usa 4 fontes (bead + git history + runtime medido + código integrado):
comando exato, cwd, exit code, output decisivo; desviou = corrige o bead, nunca a prova.

## 3. Mapa de ativos

| Ativo | Caminho / ID | Status de verdade |
|---|---|---|
| Plano canônico | `agents: docs/plans/20260910-governance-runtime-program.md` | vivos, tabelas 5a/5b/5c + Autocrítica + DoD |
| Handoff | `agents: docs/plans/20260911-handoff-governance-runtime-program.md` | este arquivo |
| Épico | beads ag-zrh (+ .2 distribuição, .3 corte temático, .4 prova) | aberto |
| Verde                | bead ag-ey2k | branch fix/green-baseline @ d590d1cfb |
| CRG sync (P0)        | bead ag-nq7q | RED medido; fix owner ai-hub |
| Esteira global       | bead ag-q4w1 | aguarda aprovação |
| Piloto homologação   | bead ag-m9lu | blocks: ag-q4w1 |
| agentsctl            | beads ag-7hz (P0), ag-blh | não iniciado |
| Forgots de registry  | beads ag-fwdu (P1), ag-xqls (P2) | abertos |
| DP entregas (ADR 0017-0020) | beads ag-p4a.1..5 | outro WS ator dev |
| Worktree verde       | `~/ai-hub-wt/green-baseline`, branch `fix/green-baseline`, origem `current-pointer-transport` | em uso |
| Worktree pointer     | `~/ai-hub-wt/current-pointer-transport` | 4 commits walker/pointer |
| Worktrees agents     | `worktrees/<lane>` (gitignored) | aposentar pós merge |
| Integração           | ai-hub: dev (merge `--no-ff`); agents: dev | 0.5.0 já no dev do ai-hub |
| CRG                  | `~/.code-review-graph/` (graph.db, registry.json, watch daemons) | RED: sync (ag-nq7q) |
| 2 RED externos adotados | `e2e deployed-services` (unidade inativa deste host) e `hook_rules operator-budget` | beads com evidência com/sem diff |

## 4. Lições/leis usadas como base (bg prime carrega)

- lane-worktree-anywhere-living-plan-law; beads-verification-triangle; BD memory `env -u BEADS_DOLT_SERVER_DATABASE`
- runtime-is-reality, distribution-routing (ADR-0015), session-governance, anti-hardcode, fix-forward
- generated files: regra via SSOT codegen config + make gen ×2 fixed-point — nunca hand-edit em `ast-grep-rules/`/`sgconfig.yml` gerados
- make verbs: Apply=Y; CRG CLI = read-only (`impact/query/refactor rename/dead-code --json/large-functions`)

## 5. Estado do grind (nums das classes)

| classe | valor | nota |
|---|---|---|
| namespace | 1100 | DI no composition root; '\\' → p.AiHub.ForgeRouting; helpers aninhados; 9 xs em test files e scripts |
| codemod   | 1033 | 197 detection-only (mod-findings.json por rule_id); recursive-type-alias _models/learning.py:11; ban-test-doubles 35 |
| pyrefly/pyright/mypy/lint | 146+40+16+42 | typing via t./p. |
| silent-failure | 40 | catch/normalize a exterminar |
| docs_make_verbs | ✅ 9 passed | 12 docs `WHAT=` aposentados consertados |

## 6. Sequência executável (grande memória do plano)

1. CRG sync (ag-nq7q) → check exit 0
2. `merge --no-ff origin/dev` na fix/green-baseline → re-medir
3. burn-down por classe (silent-failure → namespace (DI) → codemod (SSOT regras + gen ×2) → testes (migração 102+35) )
4. PR + merge dev ai-hub (ag-m9lu 7 critérios measuráveis) → deploy recovery → receipts+
5. agentsctl sync (ag-7hz) → sonda R1/F3 (ag-zrh.4) → pousar (agents) + fechar épico com 4 fontes; aposentar tudo (resíduo zero)

---
Gerado na sessão 2026-09-11 (opencode). Nova sessão: este arquivo + bd prime + plano canônico = tudo que é preciso.
