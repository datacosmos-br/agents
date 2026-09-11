# Delivery Contract & Behavioral Law Program — Plano Aprovado (v3)

Lane: `feat/governance-runtime-program` (repo `agents`, integração `dev`).
Autoridade: operador, 2026-09-10 — monopólio total do tema, absorção de
qualquer trabalho em progresso relacionado, proibição de implementação
paralela (refactor-in-place codificado em ADR-0017).

Absorve e complementa `20260910-governance-runtime-program.md` (ag-zrh):
F0/F2 concluídos permanecem; a parte de distribuição (ag-zrh.2) é assumida
por este programa; a parte ai-hub da F1 vai para o planejamento ai-hub via
prompt na seção 5.

## Status executado (evidência: comando, exit, output decisivo)

Lane ativa: `feat/delivery-contract-program` em worktree dedicada
`worktrees/delivery-contract-program` (isolada do checkout compartilhado).
Lane antiga `feat/governance-runtime-program` foi deletada local e
remotamente por ator concorrente; commits recuperados do object store e a
lane remota recriada sob o novo nome (bug bead ag-p4a.11).

| # | WS | Status | Evidência decisiva |
|---|----|--------|--------------------|
| 1 | WS-A — ADR-0017 behavioral conscience | ✅ DONE (código+pouso pendente no PR) | Commit `c4403561`: emendas professional-integrity/engineering-core; novas change-consequence + operator-alignment no bootstrap; mediação de cápsula medida 9764/10000; `make check` exit 0; `test-full` 4/4 |
| 2 | WS-B — ADR-0018 linha 0.5.0 | ✅ DONE | Adotado pelo ator em `382b490f`; `make check` exit 0 com wheel 0.5.0 provado (artifact gate + mypy strict) |
| 3 | Correção do operador (listas/proibições, incl. tests) | ✅ ABSORVIDA | `delivery.py` grammar-only (sem vocabulários fechados); teste com pin exterminado e substituído por derivação (`test_catalog_structure.py`, ator adotado); waza floor adotado; engineering-core emendado — commits `29a7de58`, `40f47818` |
| 4 | WS-C — ADR-0019 delivery contract | ✅ DONE (código+pouso pendente no PR) | Commit `29a7de58` + fmt: gate tipado de cápsula em `load()` (falhou ao vivo 2× e mediou: 9477/9488, headroom 11); eventos grammar-validated (config é dono das instâncias); docs linking gate (bijeção 16 ADRs); marcador ADR-0015; Task 3 do .kilo medida como já implementada (testes fixam) |
| 5 | Gates na worktree dedicada | ✅ GREEN | `make check APPLY=Y` exit 0 (docs/static 29/waza 128/128/wheel 0.5.0+mypy strict); `test-full` 10/10, 0 warnings/skips, testmon integrity ok |
| 6 | WS-D — ADR-0020 advance command + dossiê | ⏳ PENDENTE | Próximo: comando + dossiê 13 fontes |
| 7 | Pouso | ⏳ PENDENTE | PR → dev → review → --no-ff → prova pós-merge → beads com 4 evidências |

## 1. Fundamentação (13 fontes, dossiê em `docs/research/agent-instruction-design.md`)

- Hierarquia de autoridade explícita → Model Spec OpenAI (chain of command).
- Persistência + tools-antes-de-adivinhar + planejamento → +20% SWE-bench
  (GPT-4.1 guide); recência: não-negociáveis reafirmados no fim.
- Bloat faz ignorar regras; ênfase só na regra crítica (Claude Code best
  practices); info crítica degrada no meio (Lost in the Middle).
- Instruções verificáveis programaticamente (IFEval) → gates de máquina.
- Skills = progressive disclosure em 3 níveis (Anthropic Agent Skills);
  menor conjunto de tokens de alto sinal; altitude certa (context engineering).
- Retomada = paginação de estado (MemGPT) + reflexão verbal (Reflexion)
  + checkpoint em vez de reinício (multi-agent research system).
- Verificação executável fecha o loop ("looks done" não é sinal); revisão
  adversarial em contexto fresco; evidência > asserção.
- Eventos de ciclo de vida tipados → Claude Code Hooks reference:
  SessionStart[startup|resume|clear|compact|fork], UserPromptSubmit,
  PreToolUse/PostToolUse, SubagentStart/Stop, PreCompact/PostCompact,
  InstructionsLoaded[...|compact], SessionEnd.
- Princípios + crítica→revisão controlam comportamento (Constitutional AI)
  → valida o loop garantias→donos→emenda (ADR-0011).
- Context editing + memória externa: +39% desempenho, −84% tokens (Anthropic
  context management) → PostCompact reinjeta cápsula; estado vive em
  bead/arquivo, nunca só no resumo do provider.

## 2. Auditoria do sistema de projeção (idealizado vs implementado)

| Aspecto | Idealizado | Implementado | Gap |
|---|---|---|---|
| Cápsula por evento | hooks entregam cápsula em session start/prompt/compaction/subagent (`session-governance.md`) | dados prontos (bootstrap, capsule_summary, LawSurface) mas nenhum contrato de evento como dado | contrato `delivery` |
| Orçamento de cápsula | teto físico 10.000 chars do hook (`rules.py`) | nenhum gate tipado (só skills têm orçamento) | gate em `load()` |
| Render/injeção | ai-hub (ADR-0008) | zero código aqui por design | contrato consumível |
| Loop de aprendizado | ADR-0011 garantias→donos | 63 keys + waza 128 suítes | runtime é ai-hub |
| Ligação de documentos | grammar tipada approvals.py | README ADR manual, links de docs não validados | gate docs |

## 3. Workstreams (ADR-0017..0020) — neste repositório

### WS-A — ADR-0017 `behavioral-conscience` (PR 1)
- `rules/ethics/professional-integrity.md` emendado: cláusula de
  primordialidade (ética > prazo, custo, conveniência e qualquer orientação)
  + enquadramento de consequência (mentir/fabricar/esconder bloqueio é o ato
  mais grave — destrói a confiança que torna o agente utilizável);
  `capsule_summary` atualizado; tags → `decision:ADR-0017`,
  `effective:2026-09-10`.
- `rules/architecture/engineering-core.md` emendado: cláusula
  refactor-in-place — melhorar o dono existente no lugar; escrever
  alternativa paralela ao dono é violação; consumir a projeção, nunca
  copiar (capsule_summary + corpo). Autoridade de correção do operador
  ("parem de pedir refactor sem paralelo") codificada aqui.
- NOVA `rules/ethics/change-consequence.md`: mudança incorreta/incompleta/
  quebrante = responsabilidade autoral (detectar, corrigir, prevenir
  recorrência, assumir ao operador — nunca atribuir a outro agente ou
  contexto); mudar só o que o pedido exige; provar por gates nativos antes
  de alegar done. Sem duplicar engineering-core (uniqueness `rules.py`).
- NOVA `rules/coordination/operator-alignment.md`: realizar o pedido do
  operador sempre mesclado com plano/orientação vigente; pesquisa antes
  (docs, skills, fontes canônicas + internet); dúvida real → parar e
  perguntar; apoio como obrigação (desbloquear outros agentes e o operador,
  nunca descartar/sabotar trabalho alheio, compartilhar evidência e caminho).
  Referencia `operator-precedence`, `session-governance`,
  `fix-forward-collaboration` — sem duplicar corpos.
- `config/governance.json`: as 2 regras novas em `bootstrap.rules`
  (ordenado); garantias `consequence-aversion`, `operator-alignment`.
- Mediação de orçamento MEDIDA: prelude + 9 capsule_summaries + índice
  router < 10.000 chars (output no PR). Gate tipado chega no WS-C.

### WS-B — ADR-0018 tag reform (PR 2)
Reforma de tags + bump `0.5.0` (quebra gramática antiga; release consumida
pelo ai-hub).

### WS-C — ADR-0019 `delivery-contract` (PR 3)
1. Gate tipado de orçamento em `GovernanceBundle.load()`: soma cápsula
   (prelude + bootstrap summaries + índice router) ≤ teto declarado;
   falha loud; tests fixando o teto.
2. Contrato de eventos como dado validado: `SessionStart[*]`→cápsula
   completa; `UserPromptSubmit`→precedência; `PostCompact[manual|auto]`→
   cápsula + lista de restauração; `SubagentStart`→subconjunto de
   autoridade; `InstructionsLoaded`→corpos por routing; `SessionEnd`→harvest
   ADR-0011.
3. Gate de ligação de documentos: tabela ADR bijetora com arquivos; owners
   `document:` resolvem; links relativos em `docs/` resolvem; emenda a
   `rules/architecture/artifact-composition.md` com o mapa da gramática de
   ligação (evidência é referenciada POR ADR, nunca autoridade).
4. Reconciliação do marcador local `managed-by` vs ADR-0015.
5. Garantias novas: `capsule-budget`, `delivery-contract`.
Lei do código novo: clean-architecture (política sem I/O, tipos nos
limites, nenhuma camada vazia/interface sem consumidor real, consumers
reescritos e caminho antigo deletado no mesmo change, direção de import
provada).

### WS-D — ADR-0020 `advance-command` (PR 4)
- `commands/implementation/advance.md`: verbo único de retomada + avanço
  forçado. Fases: 0 autoridade (AGENTS.md → law skill da branch → scope
  AGENTS.md → bead); 1 retomada (estado mínimo do bead+git: objetivo,
  evidência, escopo, exclusões, trabalho concorrente, primeiro gate
  vermelho, próximo passo); 2 reflexão do último gate vermelho; 3 loop de
  avanço (persistência, tools antes de adivinhar, planejamento entre
  passos, escala de esforço explícita, subagentes só descoberta, $ARGUMENTS
  = foco); 4 verificação executável por passo (RED explícito); 5 pouso
  gitflow + zero resíduo; não-negociáveis reafirmados no fim (recência).
- Roteamento de skills (deltas de stack ficam nas skills donas, nunca
  duplicados): search-first, yagni, ssot, solid, clean-architecture,
  simplify, dry, anti-hardcode, fail-fast (código); arch-docs, doc-criteria
  (docs); verification-loop, make-check (gates); fix-forward,
  sprint-closure, release-closeout (pouso); plan-focus-recovery,
  strategic-compact, context-canary (retomada); op-learning (correções);
  branch-matched law skill (Python/FLEXT).
- `docs/research/agent-instruction-design.md`: dossiê das 13 fontes como
  EVIDÊNCIA (nunca proposta como arquitetura corrente), template via
  doc-criteria, metadados Version/Last-Updated/Related, owner
  `document:` da garantia `instruction-design-evidence`.

## 4. Fluxo de execução

Beads (épico + filhos, absorvendo ag-zrh.2) → lane atual → WS-A..WS-D com
gates por workstream (`make gen APPLY=Y` ×2 fixed point, `make audit`,
`make check APPLY=Y`, `make test APPLY=Y` via testmon persistente) → PR →
dev → review → `merge --no-ff` → gates no SHA mesclado → prova pós-merge
`GovernanceBundle.load()` → beads fechados com 4 evidências (registro, git,
comando/exit/output, código integrado) → `op-learning` registra a correção
refactor-in-place como primeiro finding completo do loop.

## 5. Contraparte runtime (ai-hub) — prompt de planejamento

> Depende do release `agents-governance>=0.5.0` com o contrato `delivery`.
> Consumir APENAS via `GovernanceBundle.load()` (ADR-0008).

```markdown
# Runtime delivery contract — consume agents-governance 0.5.0 and close the projection loop

You are planning and executing the runtime half of the governance delivery
contract. The semantic half lands in the agents repository as ADR-0017..0020
(behavioral law, tag reform, `delivery` contract with capsule budget +
lifecycle event map, `advance` command). This repo owns every runtime effect
(ADR-0008). Do not duplicate, guess, or reimplement the contract — consume it.

## Phase 0 — Authority and dependency preflight (no effects)
1. Resolve authority: workspace root AGENTS.md → branch-matched law skill →
   nearest scope AGENTS.md → active bead. Operator request > orchestration
   contract > tracker > ADRs > skills > docs > defaults.
2. Dependency gate: verify `agents-governance>=0.5.0` is installed and
   `GovernanceBundle.load()` exposes the `delivery` contract (event→payload
   map + capsule budget). If not shipped, BLOCK on that release: file the
   beads now, implement nothing, stop after planning artifacts.
3. Map current reality before writing: hook inventory, agentsctl surfaces,
   MCP bridges, daemon restart flow, workspace watch, learning config.
   Research first; never invent APIs or flags.

## Phase 1 — Planning artifacts (beads: epic + sub-epics, enforcement/validation children)
1. Capsule renderer per event contract: SessionStart[startup|resume|clear|
   compact|fork] → full capsule (strict prelude + bootstrap rule summaries +
   skills router index) within the bundle-declared budget; UserPromptSubmit
   → operator-precedence reminder only; PostCompact[manual|auto] → full
   capsule + session-governance restore list (goal, evidence, scope,
   exclusions, accepted concurrent work, first red gate, next action);
   SubagentStart → authority-inheritance subset; SessionEnd → harvest event.
2. Provider adapter law: exact native lifecycle event when exposed,
   per-turn/pre-model equivalent otherwise; never claim a semantic the
   provider does not expose. Hooks are delivery mechanisms, never policy
   owners. Typed ports at the provider boundary; adapters outside; compose
   at the executable edge — never an empty layer or interface without a real
   consumer and variation.
3. agentsctl sync: regenerate managed instruction projections from the
   bundle; managed-by + managed-version markers; sweep markerless/
   version-drifted files via retire globs; atomic replace with
   two-generation fixed point.
4. Learning loop runtime (ADR-0011): SessionEnd capture → typed Finding →
   route by guarantee keys → owner artifacts; learn verbs operational;
   operator corrections enter with authority operator-explicit; findings
   owned by rules/skills/commands become cross-repo PRs into the agents
   repository through its law — never local edits there.
5. Reconciliation: workspace/worktree watch feeds the same funnel; MCP/stdio
   bridges keep virtualized session identity across daemon restarts.

## Phase 2 — Execution law (non-negotiable)
- Refactor in place: improve existing owners; a parallel implementation,
  renderer, or registry alongside the owner is a violation. Zero residue:
  superseded code, configs, hooks and docs deleted in the same change.
- Root Make verbs only, APPLY=Y as the sole mutation flag.
- Fail loud: no catch/retry/fallback/normalization; first exception escapes
  with raw traceback. Warnings, skips, empty output, missing tools are RED.
- Evidence contract per claim: exact command, cwd, exit code, decisive
  output. Unit/integration gates never require auth keys or live model calls.
- After MCP or daemon changes: validate in-process first, then ask the
  operator to restart the Cursor MCP client before claiming client green.

## Phase 3 — Landing and closure
Scoped commits → fast-forward push → PR → resolved review → --no-ff merge
into the declared integration lane → gates rerun on the merged SHA → runtime
proved on the integrated state → release/deploy/activation with distinct
evidence → beads closed with four evidences. Dogfood the loop: the first
harvested finding is this cycle's operator correction (refactor-in-place),
routed to its guarantee and owner.

Load the branch-matched owning skill before executing each step; lightweight
subagents for discovery only; the main thread owns sequenced effects. If a
rule here conflicts with ai-hub law, stop and present both with numbers.
Execute to the end.
```
