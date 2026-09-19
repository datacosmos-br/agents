---
description:
  Fleet landing cycles follow root cause, tag-line authority, canonical commands,
  integration closure, and unmasked validation.
capsule_summary: |
  Fleet landing: suppress no warning without removing the duplication that
  caused it; version lines follow the declared tag timeline; commands execute
  only from canonical docs plus measured evidence; a cycle closes only with a
  no-ff merge on the integration lane, verified deploy, lane retirement, and
  bead evidence; pipelines never mask a producer's exit code.
metadata:
  aihub.tags: '["decision:ADR-0011","effective:2026-09-10","route:personal"]'
---

# Correções do operador — ciclos de landing da frota (2026-09-08/10)

Correções de alta autoridade com escopo declarado, extraídas dos ciclos de landing da
cidade `~/gc`. Escopo: operações de landing/integração em rigs da frota. Não generalizar
para outros domínios sem nova ordem.

1. **Causa raiz, nunca o mensageiro.** Suprimir um warning (ex.: `shadow = "silent"`)
   sem eliminar a duplicação que o gerou é violação. O conserto remove a causa; o
   warning some como consequência.
2. **Linha de versão: autoridade é a linha do tempo de tags/releases.** Não inventar nem
   adotar identidades de linhas descontinuadas; antes de bumpar, ler as tags (ex.:
   dc3→fd1→fd2→fd3) e seguir a linha viva declarada pelo operador.
3. **Comando sem base canônica não executa.** Toda ação parte dos docs/skills oficiais
   do projeto e de evidência medida (comando, cwd, exit, saída decisiva). Adivinhação de
   flag, comando ou semântica é violação.
4. **Ciclo fecha na branch de integração.** Entrega sem merge no-ff na lane de
   integração + deploy verificado não é entrega. Lane → PR → correção → merge no-ff →
   aposentadoria de lane/branch/worktree → bead fechada com evidência.
5. **Validação não mascara produtor.** Pipelines (wc/grep/tail após um comando) não
   substituem o exit code do produtor; falha de produtor invalida o PASS. Claims de
   suíte (ex.: "12/12") com falha mascarada são retirados com retificação explícita no
   bead.
