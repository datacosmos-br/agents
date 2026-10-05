---
description:
  Strict typed quality — ruff/mypy/pyright/pyrefly with u,m,p,t,c helpers, DRY
capsule_summary: |
  Universal law (operator ruling 2026-09-16): fix ruff, mypy, pyright, pyrefly
  with STRICT typing; prefer helpers, models, protocols, typings, and constants
  declared in the u, m, p, t, c namespaces, consumed the most DRY way. SSOT,
  YAGNI, DRY, DI, FLEXT, PEP, and Pydantic are mandatory and strict. Fix
  everything the newest and improved way: no fallback, no legacy, no
  compatibility — exterminated, rewired, and revalidated functioning in the
  real cluster (dc-dese). Fix forward; never discard independent work.
  Periodically sync with the integration branch via merge --no-ff.
metadata:
  aihub.tags: '["decision:ADR-0037", "effective:2026-10-05", "route:both", "supersedes:ADR-0021"]'
---

# Strict typed quality through the FLEXT facades (universal)

1. Ruff, mypy, pyright, and pyrefly run strict; violations are fixed at the owner with
   precise types, never blanket-ignored. The only FLEXT Mypy exception is the explicit
   operator policy in [Pydantic 2 boundary law](../python/pydantic.md#flext-mypy-policy);
   it does not weaken the other checkers or runtime validation.
2. Reach for helpers, models, protocols, typings, and constants declared in the `u`,
   `m`, `p`, `t`, `c` namespaced facades first, DRY-ly; declare new ones at the owning
   family when missing.
3. SSOT, YAGNI, DRY, DI, FLEXT family shape, PEP, and Pydantic-2 are mandatory and
   strict.
4. Fix everything the newest and improved way: no fallback, no legacy, no compatibility
   surface — exterminated, rewired, and revalidated functioning in the real cluster
   (dc-dese). Fix forward: do not discard work through historical or destructive
   rollback. Correct proven checker regressions only through the new-commit,
   causal-hunk restoration defined by the Pydantic policy above; preserve independent
   corrections and revalidate the resulting public behavior.
5. Periodically sync with the integration branch via `git merge --no-ff` to never fall
   behind.
