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

  Phase-end landing (operator order 2026-10-24, standing authorization): every
  phase ends committed, merged --no-ff and landed by PR into each touched
  project's integration branch, the whole reassessed on the merged SHA and the
  correlated bead closed with evidence; the live agents agree a stable
  checkpoint over mail and one designated lander performs the landing.
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

## Phase-end landing at a coordinated checkpoint

Operator order, 2026-10-24 (tracker memory
`operator-ruling-2026-10-24-phase-end-landing`), standing authorization for every
session and agent: "VC TEM QUE FAZER SEMPRE COMMIT, AVANÇAR, fazer merge no-ff,. PR com
as branchs de integracao, de todos os projetos, ao final de cada fase, autaliando o todo
e fechando a bead correlacionada (obrigatório ...) e com estabilzacao coordenada entre
todo os agentes, vc tem sempre esta autorização, só defina um checkpoint estável com os
outros agetnes para um de voces fazer isso sempre".

1. Every phase ends landed. Each session commits its scoped work, merges the integration
   base into its lane with `--no-ff`, and the phase lands through a PR into the
   integration branch of every project it touched — members first, then the umbrella
   gitlinks in a separate commit. No phase opens the next one with unlanded work.
2. Landing happens at a stable checkpoint agreed between the live agents over the mail
   channel (`inter-session-mail`, rule file): each agent announces its checkpoint SHA
   per project, the agents converge on one consistent set, and exactly one designated
   lander merges that set. The others do not merge in parallel; they keep working on top
   of the checkpoint and adopt the landed tip with `--no-ff`.
3. The lander reassesses the whole at the landed tip — gates and runtime on the merged
   SHA per `production-readiness` (rule file) — and only then closes the correlated
   bead with four-source evidence (`beads-verification`, rule file). A red found there
   keeps the phase open and is fixed forward before the next checkpoint.
4. This authorization is standing: no session asks again for permission to commit,
   merge `--no-ff`, open or merge the phase PR, or close the proven bead. It never
   authorizes rebase, force-push, squash, or landing past a red gate.
