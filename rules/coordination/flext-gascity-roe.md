---
metadata:
  aihub.tags: '["decision:ADR-0036","effective:2026-10-04","route:personal"]'
---

# Flext × Gas City rules of engagement

One fleet, two governing layers. Flext law governs how Python code is written in any
lane of any repository. Gas City law governs orchestration: cities, rigs, lanes,
dispatch, Beads, evidence, closure. This rule harmonizes their coexistence; it only
references the single declarations and never restates them.

## Authority and composition

- Precedence is fixed: operator order > city `AGENTS.md` > rig `AGENTS.md` > Beads >
  governance bundle. The newest operator instruction wins inside that order.
- Core composition: the AIHUB prelude is the shared base; flext's
  UNIVERSAL-GOVERNANCE core is the flext-domain delta on top, consumed in the order
  declared by `rules/flext/session-router.md`. Never merge the cores into a fourth
  copy; fix drift at the owning source and re-project.
- Language boundary: flext architecture law (facades `c/t/p/m/u` plus operational
  `r/e/x/h/d/s`, reverse imports TYPE_CHECKING-only, one `api.py` MRO per package,
  thin CLI adapters, declaration-only Pydantic 2 models, validate external input
  once, canonical config singleton) applies to Python sources in every fleet
  repository. Go repositories (gascity, beads) follow idiomatic Go, their own
  `AGENTS.md`, `TESTING.md` where the repository ships one, and their root Makefile;
  no flext facade applies to Go. Only the process law is shared across languages:
  dedicated worktree, bead, PR, `merge --no-ff`, never rebase.

## Green ladder, mapped

- Local per-file iteration uses the repository's scoped P0 gate (`make p0 FILE=<path>`
  where provided: fmt + fix + mod + check + smells on that file); otherwise the
  repository's own canonical verbs own the equivalent scope.
- Heavy gates (whole-program type checkers, full suites, build) run in CI on the open
  pull request. Open the PR early: CI runs in parallel while local gates close, and
  the PR is a coordination surface, never merge authorization.
- Green is never waived, only timed. Admin-merge before CI green (operator order
  2026-10-03) changes when green is measured, not whether: gates re-run on the merged
  SHA, the runtime proof executes, and the import/publication probe validates before
  any closure claim. Auto-merge never substitutes the post-merge probe.
- The zero-violation code gate has one declaration:
  `rules/workflow/canonical-commands.md` — `make mod` before new code is accepted;
  `make fmt`, `make fix`, `make check`, `make mod`, and the spelling gate clean at
  closure. The flext `smells` gate (qlty, block mode) is an additional structural
  gate in flext-family repositories; it is not the spelling gate.

## Campaign discipline (promoted from CONTROL §9.8, durable 2026-10-04)

- During a campaign, all fleet `make`/gate work flows through ONE serialized actor.
  The coordinator and every other agent stay out of `gc`/`bd` while that queue runs.
  Root cause: per-rig Dolt contention on the city store killed two agents
  (2026-10-03). Bead writes stay sequential and coordinator-only.
- Agent cutoff: an agent counts as active only with a gc-mail message dated on or
  after the current campaign cutoff (2026-10-02 at declaration). Older agents are
  abandoned — close or claim them with evidence, never by assumption.
- Every landing: PR, `merge --no-ff`, gates on the merged SHA, runtime proof, Bead
  evidence. A lane starts at the integration tip via `merge --no-ff` of the base.

## Simplification doctrine pointer

Code simplification is governed by flext law, not by this rule: strict
facade/SSOT/DI/YAGNI compliance deduplicates by itself; exterminate violations at
their owner, rewire consumers, and delete the superseded path in the same cycle;
codemods through `make mod` precede manual edits; refactorings land LOC net-negative.
See `rules/architecture/engineering-core.md` and
`rules/flext/generator-declarations.md`. This rule invents no numbers and no verbs.
