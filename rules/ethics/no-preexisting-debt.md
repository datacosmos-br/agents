---
description: No preexisting debt — every failure is owned and fixed at the root
capsule_summary: |
  "There is no preexisting failure." Any failure surfaced while working —
  yours, a sibling lane's, or left by a prior session — is corrected at its
  root with criticality elevated; it is never classified out of scope,
  deferred as someone else's debt, bypassed, or worked around with a
  fallback. `--no-verify` and any gate bypass are prohibited. Rollback is
  not a fix: correct or optimize forward.
metadata:
  aihub.tags: '["operator-ruling:2026-10-30","route:both"]'
---

# No preexisting debt

Operator ruling 2026-10-30 (session `sess_816286c6` unification, gen-perf campaign;
SSOT handoff `devops-oud-iac/docs/handoffs/20261030-gen-perf-rope-cures.md`):

1. **"Não existe falha pré-existente"** — there is no such thing as a pre-existing
   failure. Every failure encountered while working — introduced by this session, by a
   sibling lane, or left behind by a prior session — is owned here and now: diagnose the
   root cause per
   [causal diagnosis](../workflow/runtime-is-reality.md#causal-diagnosis) and fix it at
   the root, with criticality elevated (a red gate blocks the task until cured or the
   owner's blocking decision is recorded).
2. **No bypass, no fallback** — `--no-verify` is prohibited outright (see
   [gitflow branch/PR](../git/gitflow-branch-pr.md)); gate workarounds, invented rules,
   and fallback paths are prohibited per
   [professional integrity](professional-integrity.md). Honest green gates only.
3. **Fix forward, never rollback** — when the failing surface is upstream or generated
   work in flight (WIP of a parallel lane, generated code, a backend dependency),
   correct or optimize it forward; reverting is a violation even for generated trees
   (see [fix-forward collaboration](../coordination/fix-forward-collaboration.md)).
4. **Adopt before edit** — when the failing surface belongs to an active lane, adopt
   the lane's current contract first, then fix; never patch against a superseded
   contract.

Precedent from the ruling's session: a `make check` blocked by a stale test using
superseded kwargs was adopted and updated to the current contract, not skipped; 23
pyrefly findings in a prior session's file (`backup.py`) were narrowed at the union
member instead of ignored; three commits that had used proof-per-file `--no-verify`
were accepted only because they predated the ruling, and the ruling made every
subsequent gate honest.

Compose with [professional integrity](professional-integrity.md),
[change consequence](change-consequence.md),
[strict typed quality](strict-typed-quality.md).
