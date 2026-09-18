# ADR-0022 — Home global `~/.agents` como projeção materializada versionada

**Status:** Accepted (emendado 2026-09-18 — errata G0) **Date:** 2026-09-18 **Scope:**
`~/.agents` (superfície de leitura global) · gestão: **AI Hub** ·
`docs/plans/20260918-handoff-repasse-consolidado.md`

## Context

`~/.agents` é hoje um **symlink para o checkout fonte** `/home/marlonsc/agents`. O
diagnóstico do rework de distribuição aprovado em 18/09 (seção §6, F6) mediu o risco:
`make gen` reescreve config viva do usuário dentro do checkout; `git clean`/switch de
branch no fonte pode deletar o home; hooks de dois donos (ai-hub × Gas City) convivem
nos mesmos JSONs projetados. A separação completa (home como transação do ai-hub) é a
F6 do rework e pressupõe F1–F3 do ai-hub — hoje vermelhos. Enquanto isso, todo consumo
catálogo-side (session-router, skills globais, waza) resolve por `~/.agents` e fica
exposto a esse acoplamento.

Decisão do operador (2026-09-18, esta campanha): o home deixa de ser symlink **nesta
campanha** e passa a ser **projeção global materializada** — fallback de leitura
universal para todos os projetos e agentes — **gerenciada pelo AI Hub**, não mais como
alias do checkout.

## Decision

1. **Projeção de leitura universal, fonte única no repo.** `~/.agents` materializa o
   catálogo semântico do checkout (`skills/`, `rules/`, `commands/`, `agents/`,
   `evals/`, `docs/adr/`, `docs/research/`, `docs/security/`, `AGENTS.md`,
   `README.md`, `metadata.json`) — e nada mais: nenhum `.git/`, `.venv/`, `.beads/`,
   `.gc/`, `worktrees/`, `dist/`, superfícies de provider do checkout (`.claude/`,
   `.codex/`, `.cursor/`, `.gemini/`, `.opencode/`, `.kilo/`) nem config viva de
   usuário. `AGENTS.md` entra por consumidor medido: é alvo declarado do
   `ssot_relink` e da gate fail-closed `projection_identity_gate` do ai-hub
   (`config/governance.yaml:10-16`). Consumidores lêem; nenhum consumidor escreve —
   escrita de consumer no home é defeito reportado, não estado aceito.
2. **Carimbo de versão + digest (P5/ADR-0015).** O home carrega
   `.agents-governance.json` com `owner`, versão do bundle, `generated_at` e digests
   por árvore. Convergência se decide por versão+digest, nunca por byte-diff cego.
3. **Gestão é do AI Hub (emenda G0).** A única ferramenta sancionada para
   materializar/verificar o home é a transação de deploy do **ai-hub** (surface
   catalog-home da F6 do rework de distribuição). **O repo agents não carrega
   ferramenta, verbos de Make nem gate de home** — ele é catálogo read-only puro
   (ADR-0008); a cláusula original que criava `tools/home_projection.py` +
   `home-sync`/`home-check` está **REVOGADA** (criava um mecanismo de distribuição
   paralelo ao ai-hub).
4. **Estado transicional (até o ai-hub assumir):** cópia estática materializada em
   18/09 (backup do symlink em `~/.agents-archive/home-desymlink-2026-09-18/`),
   com manifesto já no formato ai-hub; risco de stale documentado; o reparo do stale
   é a gestão ai-hub assumir — **nunca restaurar o symlink**.
5. **Transição com backup.** Remoção do symlink precedida de backup tar datado +
   MANIFEST (doutrina: exclusão fora do git só com backup). O reparo de qualquer
   falha pós-transição é forward (gestão ai-hub), nunca restauração do symlink.

## Consequences

- O checkout fonte deixa de ser ponto único de falha do home: `git clean`/branch
  switch não tocam mais o que os consumidores leem.
- `make gen` do checkout volta a escrever somente superfícies do próprio checkout; a
  config viva do usuário (hooks Gas City × ai-hub) sai do raio de efeito colateral.
- Drift catálogo×home fica visível quando o ai-hub assumir a verificação
  (`projection_identity_gate` já fail-closed); no intervalo, o stale é conhecido e
  aceito como estado transicional declarado.
- A gestão transacional final é do ai-hub (F6 do rework); a fronteira
  **flext ⊄ privado / privado ⊇ flext** permanece: nada disto cria dependência do
  flext para com agents/ai-hub.
