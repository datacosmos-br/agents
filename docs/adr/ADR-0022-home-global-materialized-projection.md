# ADR-0022 — Home global `~/.agents` como projeção materializada versionada

**Status:** Accepted **Date:** 2026-09-18 **Scope:** `tools/home_projection.py`,
`Makefile` (verbos `home-sync`/`home-check`), `docs/plans/20260918-status-ledger.md`,
manifesto `.agents-governance.json` do home

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
universal para todos os projetos e agentes — gerenciada pelo par ai-hub/agents, não
mais como alias do checkout.

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
   `.agents-governance.json` com `owner`, `distribution_version` do bundle,
   `generated_at`, e digest SHA-256 por árvore de artefato. Convergência se decide por
   versão+digest, nunca por byte-diff cego.
3. **Ferramenta dev-only, fora do pacote (ADR-0008).** `tools/home_projection.py`
   materializa e verifica; o pacote publicado continua sem projector/home-writer.
4. **Gates via Make raiz.** `home-sync` re-materializa (idempotente, com receipt
   impresso); `home-check` compara digest projeção×catálogo e falha loud em drift —
   wired no `check`. Enquanto o ai-hub não assume a gestão transacional (F6 do
   rework), esses verbos cobrem o risco de stale silencioso.
5. **Transição com backup.** Remoção do symlink precedida de backup tar datado +
   MANIFEST (doutrina: exclusão fora do git só com backup). O reparo de qualquer
   falha pós-transição é forward (`home-sync`), nunca restauração do symlink.
6. **Workaround declarado.** Os verbos `home-sync`/`home-check` entram no Makefile
   como workaround local marcado, pendente de adoção pelo codegen flext-infra (lane
   paralela avisada); a adoção upstream substitui a marcação sem mudança de contrato.

## Consequences

- O checkout fonte deixa de ser ponto único de falha do home: `git clean`/branch
  switch não tocam mais o que os consumidores leem.
- `make gen` do checkout volta a escrever somente superfícies do próprio checkout; a
  config viva do usuário (hooks Gas City × ai-hub) sai do raio de efeito colateral.
- Drift catálogo×home fica visível e falha loud no `check` em vez de envelhecer em
  silêncio (estado medido em 18/09: manifesto do espelho claude 06/09 × catálogo
  18/09).
- A gestão transacional final permanece da ai-hub (F6 do rework); este ADR é o
  estado intermediário sancionado, com as duas lanes — ai-hub e agents — donas do
  mesmo contrato.
