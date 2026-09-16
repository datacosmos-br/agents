---
description: Strict typed quality — ruff/mypy/pyright/pyrefly with u,m,p,t,c helpers, DRY
capsule_summary: |
  Universal law (operator ruling 2026-09-16): fix ruff, mypy, pyright, pyrefly
  with STRICT typing; prefer helpers, models, protocols, typings, and constants
  declared in the u, m, p, t, c namespaces, consumed the most DRY way. SSOT,
  YAGNI, DRY, DI, FLEXT, PEP, and Pydantic are mandatory and strict. Fix
  everything the newest and improved way: no fallback, no legacy, no
  compatibility — exterminated, rewired, and revalidated functioning in the
  real cluster (dc-dese). Always fix-forward adopt; never fallback or rollback.
  Periodically sync with the integration branch via merge --no-ff.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Strict typed quality through the FLEXT facades (universal)

1. Ruff, mypy, pyright, and pyrefly run strict; violations are fixed at the
   owner with precise types — never suppressed, never blanket-ignored.
2. Reach for helpers, models, protocols, typings, and constants declared in the
   `u`, `m`, `p`, `t`, `c` namespaced facades first, DRY-ly; declare new ones at
   the owning family when missing.
3. SSOT, YAGNI, DRY, DI, FLEXT family shape, PEP, and Pydantic-2 are mandatory
   and strict.
4. Fix everything the newest and improved way: no fallback, no legacy, no
   compatibility surface — exterminated, rewired, and revalidated functioning in
   the real cluster (dc-dese). Always fix-forward adopt; never fallback or
   rollback.
5. Periodically sync with the integration branch via `git merge --no-ff` to
   never fall behind.
