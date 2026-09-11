# reval250909 — Plano de Fechamento (adoption lane → dev)

Status: aguardando aprovação do operador (2 decisões abertas, ver fim).
Autor da execução: sessão opencode reval250909. Autorização de pouso: operador
("subir isso para a branch de integracao ao final e ele nao pode gerar erros");
merge registrado como operator-authorized (AGENTS.md lei 12).

## Estado medido (evidência, 2026-09-10)

- Lane `feat/reval250909-adoption` pousada no origin. Contém: commits do ator
  paralelo (5d02942, ff2bdf7, d0774db, 17b9b5f, 04e1de7) + bb5b02d ([WIP]
  adoção do estado da árvore) + 786e59a (correções de gate) + test(evals).
- Gates verdes NA LANE: `make setup`; `make gen` ×2 com ponto
  fixo; `make waza` (via waza_gate) verde; `make check` verde completo.
- `make ci` interrompido pelo operador antes de conclusão — único gate
  pendente.
- Tracker: dedup gate `bd find-duplicates --limit 0` = 0 pares; `bd lint` = 1
  warning intencional (ag-gmx, ator vivo); `bd doctor` = 71 passed, 1 erro
  estrutural esperado (DB compartilhado multi-projeto).
- Correções de causa raiz já na lane: split `gen build:` → `gen:`/`build:`
  (ag-645); gramática de description; tags de decisão válidas
  (ADR-0008/ADR-0014); cosmos-gitops portável (sem marca); regra
  provenance-first com lei de evidência completa; beads-canonical-epics com
  varredura exaustiva `--limit 0`; ponteiro stale → provenance first;
  duplicatas stale deletadas (verification-loop, make-check na raiz);
  inviolable-rules realocada à taxonomia canônica; 5 suítes de eval novas
  cobrindo todos os tokens de descrição (lei waza req-description-001).

## Fase 1 — CI completo (único gate pendente)

1. `make ci` com loop de lock (ator paralelo compartilha locks
   waza/testmon: poll + retry; sem bypass, sem normalização).
2. Saída: exit 0 + contagem de testes. Qualquer RED → corrigir no owner e
   repetir o gate afetado até verde.

## Fase 2 — Pouso na integração (`dev`)

1. `gh pr create --base dev --head feat/reval250909-adoption` (registro).
2. Merge `--no-ff` operator-authorized; nunca squash/rebase/force-push.
3. `git fetch origin --prune`; provar `git merge-base --is-ancestor` do base
   recém-buscado antes de qualquer aposentadoria.
4. Push de `dev`.
5. Prova pós-merge no SHA integrado: `make gen` ×2 (ponto fixo) +
   `make check`.

## Fase 3 — Aposentadoria de lanes (ciclo fechado, resíduo zero)

- Deletar `wip/beads-governance-reval250909` (conteúdo superseded pela árvore,
  comprovado por diff blob-a-disco) e `feat/reval250909-adoption` local+remota.
- Proibido `--force`; aposentadoria só após ancestor proof do passo 2.3.

## Fase 4 — Fechamentos no tracker (quatro fontes)

| Bead | Ação | Evidência exigida |
|---|---|---|
| ag-645 | DONE | `make help` lista gen/build; gates verdes |
| ag-s8r | DONE | conteúdo pousado; lane aposentada |
| ag-aq8.2 | DONE se F1+F2 verdes | gen ×2 + check no SHA integrado |
| ag-aq8 (epic) | medir ag-aq8.1 vs runtime antes de claim | prova pública de profiles |
| ag-1b5, ag-blh | re-home/defer (dono = ai-hub, artefatos medidos lá) | sem falso fechamento |
| ag-9qg | lane subsequente (pin `npm:jscpd = 5.1.2` + `make duplication` verde) | fora desta lane |

## Fase 5 — Higiene final do tracker

- `bd find-duplicates --limit 0` (0 pares) · `bd lint` · `bd doctor` ·
  `bd vc commit`.
- Regenerar `~/agents.json` / `~/agents.csv` (100% reval250909).
- Sem `bd dolt push` sem autorização explícita do operador.

## Decisões abertas do operador

1. Pouso: PR + merge operator-authorized imediato (recomendado) OU merge
   direto sem PR?
2. ag-9qg: lane subsequente separada (recomendado) OU incluir nesta?
