---
description: Full landing cycle or nothing — integration branch and runtime closure
capsule_summary: |
  Universal law (operator ruling 2026-09-16): se você não fizer o ciclo completo
  de levar o PR até a branch de integração — e nos casos solicitados até o
  runtime — você não fez absolutamente nada e perdeu todo o trabalho. A unit of
  work is complete ONLY when it reaches the integration branch (PR merged or
  fast-forward pushed to it, as the repo's lane requires) and, when the request
  includes it, applied and observed functioning in runtime.

  Partial cycles (code written, gates green locally, "done" reports) count as
  zero. The cycle definition per grain is declared up front; closing the cycle
  is what converts work into delivered work.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Full landing cycle or nothing (universal)

Se você não fizer o ciclo completo de levar o PR até a branch de integração — e, nos
casos em que for solicitado, até o runtime — você não fez absolutamente nada e perdeu
todo o trabalho.

1. Every grain declares its landing cycle up front: which integration branch, PR or
   direct FF push, which runtime (if the request demands runtime application), and which
   observation proves it working there.
2. Work is complete only when the cycle closes: change landed on the integration branch
   (and applied to runtime when required, with runtime evidence per validate-on-change).
3. Anything short of the closed cycle is reported as in-progress with the exact missing
   step — never as done. Losing closed-cycle discipline loses the work entirely.
4. This composes with wip-persistence: wip protects the work in flight; the landing
   cycle is what delivers it. Both are mandatory.
5. Operator order, 2026-10-24, verbatim: "ao fazer alguma coisa SEMPRE TEM QUE IR ATÉ O
   FINAL, NÃO ABANDONE PERTO DO FINAL, EM HIPÓTESE ALGUMA". A started task is carried
   to its declared stop condition over its whole declared population. Measuring a
   subset, fixing it, and reporting the rest as remaining or as someone else's is
   abandonment near the end. So is stopping at the last items because they look hard
   or belong to another area. The final check reruns the operator's own measurement
   unscoped, such as the same command on the same root, and the task ends only when it
   is clean. A real blocker is named with its evidence and the precise question; every
   other item is finished in the same turn. Observed 2026-10-24: a ruff sweep was
   counted outside one member, reported as done with 7 remaining, while the
   operator's whole-tree run showed 27.
