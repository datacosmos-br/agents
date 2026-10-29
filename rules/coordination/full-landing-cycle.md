---
description: Full landing cycle or nothing — integration branch and runtime closure
capsule_summary: |
  Universal law (operator ruling 2026-09-16): se você não fizer o ciclo completo
  de levar o PR até a branch de integração — e nos casos solicitados até o
  runtime — você não fez absolutamente nada e perdeu todo o trabalho. A unit of
  work is complete ONLY when its reviewed change reaches the declared integration
  branch through the current Git owner and, when the request
  includes it, applied and observed functioning in runtime.

  Partial cycles (code written, gates green locally, "done" reports) count as
  zero. The cycle definition per grain is declared up front; closing the cycle
  is what converts work into delivered work.

  Current operator publication authority persists within its declared scope;
  branch/PR owns green checkpoints and gated integration. One elected integrator records shared
  checkpoints. At the end of every phase, PRs into the integration branch of every
  in-scope project ahead of it are evaluated as a whole, merged, revalidated on the
  merged SHA, and the correlated bead is closed with evidence — mandatory.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Full landing cycle or nothing (universal)

Se você não fizer o ciclo completo de levar o PR até a branch de integração — e, nos
casos em que for solicitado, até o runtime — você não fez absolutamente nada e perdeu
todo o trabalho.

1. Every grain declares its landing cycle up front: which integration branch and
   reviewed PR, which runtime (if the request demands runtime application), and which
   observation proves it working there.
2. Work is complete only when the cycle closes: change landed on the integration branch
   (and applied to runtime when required, with runtime evidence per validate-on-change).
3. Anything short of the closed cycle is reported as in-progress with the exact missing
   step — never as done. Losing closed-cycle discipline loses the work entirely.
4. This composes with wip-persistence: wip protects the work in flight; the landing
   cycle is what delivers it. Both are mandatory. One phase at a time, never a new one
   beside an incomplete one, and where incomplete work may be pushed, are declared once
   in `rules/workflow/phase-admission-protocol.md` Laws 0 and 4.
5. Operator order, 2026-10-24, verbatim: "ao fazer alguma coisa SEMPRE TEM QUE IR ATÉ O
   FINAL, NÃO ABANDONE PERTO DO FINAL, EM HIPÓTESE ALGUMA". A started task is carried
   to its declared stop condition over its whole declared population. Measuring a
   subset, fixing it, and reporting the rest as remaining or as someone else's is
   abandonment near the end. So is stopping at the last items because they look hard
   or belong to another area. The final check reruns the operator's own measurement
   unscoped, such as the same command on the same root, and the task ends only when it
   has zero required findings. This measures the declared result, never demands a
   clean checkout. A real blocker is named with its evidence and the precise question; every
   other item is finished in the same turn. Observed 2026-10-24: a ruff sweep was
   counted outside one member, reported as done with 7 remaining, while the
   operator's whole-tree run showed 27.
6. Operator order, 2026-10-24, verbatim: "VC TEM QUE FAZER SEMPRE COMMIT, AVANÇAR,
   fazer merge no-ff,. PR com as branchs de integracao, de todos os projetos, ao final
   de cada fase, autaliando o todo e fechando a bead correlacionada (obrigatório) e com
   estabilzacao coordenada entre todo os agentes, vc tem sempre esta autorização, só
   defina um checkpoint estável com os outros agetnes para um de voces fazer isso
   sempre, isso tem que estar dentro das regras gerais e ser sempre seguindo em todas
   as sessoes e agentes". Reconciled 2026-10-29: retain this delivery and coordination
   intent through the current branch/PR owner and operator scope, not as a waiver:
   - **Authorized green checkpoints.** Complete the declared local acceptance before
     scoped publication. Existing authorization needs no repeated permission within
     its scope; it grants no incomplete working-branch push or bypass of review/CI.
   - **One checkpoint integrator.** Concurrent agents elect, through the coordination
     channel, one integrator for shared records (superproject gitlinks, stable
     checkpoints). The others post `[coord] member <repo> <sha>` per push; the
     integrator records them and marks a stable checkpoint `[checkpoint]` once the whole
     combined state is runtime-proven and lint/type clean. An integrator silent past the
     abandonment threshold is replaced by the next agent, who records and announces.
   - **Phase-end closure, mandatory.** When a phase's scope is done, the owner announces
     `[coord] phase-end <phase> <bead>`. Agents reconcile the combined candidate and
     publish only completed green checkpoints through the elected integrator; the
     integrator records a stable checkpoint; then, for every in-scope project whose working
     branch is ahead of its integration branch, a PR is opened or updated into the
     integration branch, the whole combined state is evaluated (CI plus runtime proof),
     and the PR merges with a merge commit only on green CI (operator, 2026-10-24: "PR
     merge para as branchs de integracao tem que sempre passar com o CI verde").
     Resolve review through the current approval owner; an old administrative
     exception supplies no approval for this delivery. The gates rerun
     on the merged SHA, and the phase owner closes the correlated bead with four-source
     evidence: PR URLs and merge SHAs, gates, runtime proof, and the integrated code. A
     phase with any project left unmerged or its bead open is not finished.
   - Refs are always fully qualified (`refs/heads/<branch>`): a tag or remote that
     shares the branch name makes a bare refspec ambiguous and silently stale.
