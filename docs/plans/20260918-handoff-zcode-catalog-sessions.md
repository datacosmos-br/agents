# Handoff recuperado — sessões ZCode que tocaram o catálogo (2026-09-18)

> Mandato do operador: "o último handoff de zcode foi perdido, recupere". Veredito da
> recuperação: **não houve perda de arquivo — houve não-criação.** Nenhuma sessão ZCode
> tem workspace `/home/marlonsc/agents` (índice `~/.zcode/v2/tasks-index.sqlite`
> verificado read-only); o histórico git do catálogo não registra deleção de handoff e
> o stash está vazio. O trabalho catalog-side das sessões ZCode ficou registrado apenas
> como 2 commits em `dev`, 1 doc de acordo e seções do handoff unificado do
> algar-oud-mig. Este documento consolida esse registro disperso em um handoff único.

## 1. Sessões identificadas (fonte: tasks-index.sqlite, narrativas extraídas 18/09)

| Sessão | Janela (-03) | Título | Papel catalog-side |
| --- | --- | --- | --- |
| `sess_b22e8d6c` | 13:02→15:06 | "skills, realinhe elas …" | Ciclo S3: revalidação 146/146 de artefatos (superfícies do algar; catálogo lido como autoridade e apontado com `session-router` stale) |
| `sess_a97a9cb3` | 15:09→15:39 | "Handoff unificado de 3 sessões (6334ea0c)" | Consumiu o handoff unificado e executou os follow-ups transversais catalog-side (commits abaixo); depois estendeu §10 no handoff do algar e seguiu no grind de namespace (Round 10, `2aacd982`) |

## 2. O que as sessões deixaram no catálogo (evidência em git)

1. `d08439df` — `rules/flext/session-router.md`: os 3 caminhos globais re-apontados aos
   paths canônicos do catálogo (a regra de 10/09 usava paths curtos stale; fix
   fail-closed conforme a própria regra).
2. `e735eb2e` — `docs/sync-alignment-2026-09-18.md`: acordo de sincronização de
   superfícies (catálogo `~/.agents` × ai-hub × repos FLEXT × operador) com 6 regras,
   incluindo: `~/.claude/skills` = projeção ai-hub; `synced/` = runtime Claude Code
   intocável; superfície de workspace é do repositório; consumidor `claude` em
   `inactive_consumers` = flag para a lane ai-hub.
3. Efeito colateral medido nesta campanha (F0): o `d08439df` NÃO foi o causa-raiz do
   estouro do budget da cápsula (como se suspeitou) — o reflow do prelude no commit
   `6978f43c` do próprio catálogo cresceu +40 chars. Corrigido em `a1213d2c`.

## 3. Pendências transversais registradas pelas sessões (com dono)

| Pendência | Dono | Estado |
| --- | --- | --- |
| `ai-hub deploy` bloqueado no preflight ("runtime build must contain exactly one ai-hub 0.5.0 wheel: ()", com wheel em `dist/` e build verde) | ai-hub | RED medido pela sessão; 3 variantes de cwd + build + retry exauridos; não é defeito do catálogo |
| Redeploy `ai-hub deploy --agent claude --surface skills` (espelho defasado: manifesto 06/09 × catálogo 18/09; `validate-agents` aponta `agent-browser`) | ai-hub | aguarda o item acima |
| Registro do consumidor `claude` (ativo vs `inactive_consumers`) e exclusão formal de `synced/` da governança | ai-hub | regra 5/6 do sync-alignment |
| Par `gascity.mayor`+`gc.mayor` recriado pelo runtime gc (mesmo inode, 2 slugs; ownership JSONs zerados); poda no consumidor é whack-a-mole | gc / flext-infra | handoff emitido na lane flext (`.kilo` lá é gitignored — arquivo em disco) |
| Adjudicação command-vs-router do `flext-law` na fonte flext | flext | pendente na lane |
| Bead `algar-79t` (falha real: `acl-convert` parseia 0 entradas do LDIF real com teste verde) | algar-oud-mig | citada no repasse final da sessão; trabalho algar |

## 4. Fila catalog-side herdada (consumida por esta campanha)

O estado de repasse da `sess_a97a9cb3` apontava para: ledger de beads, fechamento de
épicos com evidência, vocabulários para config-dado e a contradição contrato×código
(`AGENTS.md` no-CLI vs `cli.py`/`projection.py`). Tudo isso virou o plano da campanha
corrente (`docs/plans/20260918-status-ledger.md` e fases F2–F7). Nenhuma ação das
sessões recuperadas exige redo — apenas os donos externos acima ainda devem consumir
seus itens.
