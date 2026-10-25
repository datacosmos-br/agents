---
description:
  No rushed work — dedicated worktree/branch, status, tracker items, wip local + remote
capsule_summary: |
  Universal law (operator ruling 2026-09-16): nunca faça algo com pressa para
  concluir. Sempre atualize os status, itens do tracker; sempre grave com wip local
  e remotamente VIA SUA WORKTREE E BRANCH DEDICADA DE TRABALHO — never directly on
  the integration branch, never only in a working tree.

  Work living only in a shell or an unprotected checkout does not exist. Each
  effort runs in its dedicated worktree + branch; incomplete work is preserved
  only on a preservation ref and the working branch receives only green work
  (rules/workflow/phase-admission-protocol.md, Law 4, effective 2026-10-24);
  integration happens through the declared cycle (PR to the integration branch;
  runtime when required).
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-10-24", "route:both"]'
---

# No rushed work: dedicated worktree/branch, status, tracker items, wip local + remote

Nunca faça algo com pressa para concluir. Sempre atualize os status, itens do tracker,
e sempre grave com wip local e remotamente — via sua worktree e branch dedicada de
trabalho.

1. Rushing to conclude is a defect: a grain ends when its cycle ends.
2. Each effort owns a dedicated worktree and a dedicated working branch. Never park
   work on the integration branch, never leave it only in a working tree. Where incomplete
   work is pushed and what the working branch and its PR may receive are declared once,
   in `rules/workflow/phase-admission-protocol.md` Law 4: incomplete work goes only to a
   preservation ref, untested, and the working branch receives only green work.
3. Status and tracker items are updated at every grain boundary — before starting the
   next piece, not "later".
4. Wip is preservation, not landing: the full landing cycle (PR to the integration
   branch; runtime when required) still applies before completion is claimed.
