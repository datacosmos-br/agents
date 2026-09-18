# Alinhamento de sincronização de superfícies de agente — 2026-09-18

**Partes**: catálogo `~/.agents` (agents-governance, autoridade provider-neutral) ·
ai-hub (dono de discovery/selection/composição/deploy) · repositórios FLEXT
(algar-oud-mig etc., donos das superfícies de workspace) · operador.

**Contexto**: diretriz do operador para alinhar o plano de artifact-distribution do
ai-hub (`docs/plans/2026-09-18-artifact-distribution-rework.md`, aprovado 2026-09-18)
com o plano de execução da lane S5 do algar-oud-mig, acordando regras de
sincronização sem forkear o plano alheio.

## Regras acordadas

1. **`~/.claude/skills` é projeção do ai-hub** via governance manifest
   (`.agents-governance.json` v6, 53 entradas gerenciadas, `owner: agents-governance`).
   Nenhuma lane edita skill gerenciada diretamente; a mutação é
   `agents → ai-hub deploy --agent <id> --surface skills` → espelho.
2. **`synced/` dentro de `~/.claude/skills` é runtime do Claude Code** (sync de
   skills de conta Anthropic; manifesto interno `"source": "anthropic-example"`),
   NÃO é governado pelo ai-hub nem pelos repositórios. Intocável por todas as
   lanes; exclusão da varredura de gates é responsabilidade de quem varre.
3. **Superfície de workspace é do repositório**: `.agents/provider.toml` +
   `commands/flext-law.md` + symlinks rastreados de cada repo FLEXT (doutrina S3 do
   algar-oud-mig: "a superfície é o que o provider.toml declara + o que o gc
   projeta"). ai-hub distribui, mas não redefine o dono (mesma cláusula do
   session-router).
4. **Catálogo `~/.agents` é o canônico de skills globais**; paths de regras citam o
   catálogo por path canônico longo (fix `d08439df` no session-router). Fail-closed
   quando path exato falta.
5. **`claude` está em `inactive_consumers` do surface-catalog** — divergência com o
   fato de `~/.claude` ser projeção gerenciada ativa (53 entradas). Flag para a lane
   ai-hub reavaliar o registro do consumidor no rework de distribuição.
6. **Deploy de superfície roda do git root do repo chamador** (preflight do ai-hub
   exige identidade git); ferramentas de sync de terceiros (ex.: buckets `synced/`)
   não são alvo de governança.

## Estado apurado (evidência S5)

- Manifesto: 2026-09-06; catálogo: 2026-09-18 → espelho defasado (1 divergência
  visível: `~/.claude/skills/agent-browser/SKILL.md` conforme
  `ai-hub validate-agents --surface skills --agent claude`).
- `ai-hub deploy --agent claude --surface skills` falha no preflight de runtime:
  `runtime build must contain exactly one ai-hub 0.5.0 wheel: ()` — com wheel
  presente em `ai-hub/dist/` (build verde) e runtime `releases/0.5.0+871589867666`
  instalado. Item de handoff para a lane ai-hub (pipeline de runtime build/staging),
  não para a lane consumidora.

## Ação pendente (dona: ai-hub)

1. Corrigir preflight de runtime build do `ai-hub deploy` (wheel staging vazio).
2. Re-rodar deploy claude/skills para reconciliar `agent-browser` (e qualquer delta
   do catálogo 06→18/09).
3. No rework de distribuição, decidir o registro do consumidor `claude`
   (ativo vs `inactive_consumers`) e a exclusão formal de `synced/`.
