---
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:personal"]'
---

# Full-Standards Cleanup & Conformance Sweep (universal)

Authority order before any effect: workspace root `AGENTS.md` → branch-matched
flext-law skill → nearest scope `AGENTS.md` → active Bead. On a rig hosting a
non-FLEXT project, apply only the universal layers below (truth, evidence,
fail-fast, zero residue, canonical commands, DRY/SSOT/YAGNI) and upstream
conventions — never impose FLEXT architecture across the fleet boundary.

## 1. Truth — absolute, zero tolerance

A claim is true only with exact command, cwd, exit code, and decisive output.
Intention, self-report, "should work", "mergeable" are NOT proof. Fake green is
the most severe violation (P0). Warnings, skips, empty output, missing tools
are RED — never normalized, capped, or suppressed. The first exception escapes
with its raw traceback; no catch, retry, fallback, or normalization, ever.

## 2. Canonical command surface — never invent

Everything runs ONLY through the workspace root Make dispatcher (`setup`, `gen`,
`fix`, `fmt`, `check`, `test`, `conform`, WAZA, publication) with the single
declared mutation flag. NEVER add invented selectors (WHAT=, PROJECT=, FILE=,
MATCH=, ARGS=) beyond the dispatcher's own contract. NEVER bypass with raw
uv/pytest/ruff/mypy/ad-hoc scripts. A broken verb is a defect fixed at its owner
(generically in flext-infra), then the native verb is rerun. Diagnosis and
validation are bound by the same rule as mutation.

## 3. testmon is mandatory

Every test execution flows through the canonical testmon cache — including
explicitly requested full runs, which still go through `make test` with the
cache retained. A raw full-suite bypass is prohibited.

## 4. Root cause, zero residue, complete rewire

Fix at root cause, canonical owner, correct location, full context.
Dead/superseded/duplicate code is removed IMMEDIATELY in the same change; every
consumer is rewired to the final owner BEFORE the old one dies. No compat
aliases, shims, dual old+new paths, undone-later workarounds, or "temporary"
anything. Procedure: inventory owner/consumers/fallbacks/tests/docs → classify →
rewire consumers to the SSOT → delete old owner → regenerate managed surfaces →
prove with zero-residue semantic searches, generation fixed point, full gates.
"Pre-existing problem, not my responsibility" does not exist: every defect in
the blast radius, including pre-existing ones, is adopted and fixed. Nothing is
deferred.

## 5. Reality is the authority; tests are never SSOT

Runtime behavior and the real external contract come first. Tests validate WHAT
the system does today, never how it is implemented; when tests contradict
observed behavior, fix the tests — never bend production or freeze config.
Tests exercise ONLY public facades and observable behavior: no mocks, no patch,
no internal-construction assertions, no hardcoded project-owned values, no
copied setup. They use tm fixtures, canonical c/t/p/m/u contracts, the unified
conftest.py, and typed shared fixtures with maximum automation. Hardcoded,
non-automated test forms are prohibited outright.

## 6. FLEXT architecture law — strict, every managed project

Strict chain `settings → config → c → t → p → m → u → base.py → services/*.py
→ api.py → cli.py`; MRO facades c→t→p→m→u + operational r/e/x/h/d/s; reverse
imports TYPE_CHECKING-only. One public `api.py` per package (sole composition
root) + thin `cli.py`. Internals under `_[module]/*.py` starting with `base.py`;
`[module].py` imports all with explicit inheritance (diamond MRO). One class per
module, nested only. ≤1000 logical LOC/module.

- NO local redeclarations, aliases, or competing long-name layers: every module
  consumes settings, config, c/t/p/m/u through the canonical single-form
  imports. Found violation → delete and rewire immediately.
- **Lazy imports via `__init__` are the PREFERRED form** (performance, no
  import cycles) — implemented with the fleet lazy exports pattern
  (`build_lazy_import_map` + `install_lazy_exports`, TYPE_CHECKING imports).
  Cyclic-import errors are symptoms of strict-rule violations, fixed at the
  rule, never with path hacks or sys.path injection.
- Declaration layers are pure data; behavior only in u/base/services/api/cli.
  Pydantic-2 in/out; typing via `t.*`/`p.*` only — `Any`, `object`, `Optional`,
  dict contracts banned.
- CA/DI forever: dependencies cross boundaries only via p protocols, injected
  explicitly, wired ONCE at the composition root. Direct dependencies, service
  locators, globals, string keys, hidden singletons, import-time wiring:
  BANNED forever.
- Manual registries/mappings that duplicate discoverable structure (e.g.
  `class-nesting-mappings.yml`) are exterminated: discovery is automated from
  the SSOT, never maintained by hand.

## 7. Disciplines applied completely, in order

Per touched unit: search-first → yagni → ssot (one writable authority per fact;
canonical defaults declared once at the typed owner) → solid → simplify →
dry/jscpd (zero clones via the canonical duplication gate) → anti-hardcode
(operational values live in config/*.yaml/typed settings) → fail-fast. Apply
the full stack — settings, config, c/t/p/m/u, base, services, api, cli,
deduplication, SOLID, YAGNI, DRY, SSOT, CA, DI, and Make
setup/gen/fix/fmt/check/test — to every adjustment, completely.

## 8. Generated surfaces & commit hygiene

Never hand-edit AUTO-GENERATED files (`__init__.py`, facet roots, [MANAGED]
sections, generated config/CI/docs): change the generator/SSOT, run
`make gen`, prove idempotence. Every generated file keeps its standardized
header: how it was generated, how to adjust it, the exact regeneration rule.
Commits carry zero garbage: no debris, dead code, stale docs/comments, or
throwaway workarounds. `git add` by explicit paths only; fix-forward — never
reset/checkout/restore/clean/stash shared work. Docs updated in the SAME change
as behavior.

## 9. Self-repairing governance

Any rule, skill, command, doc, ADR, template, hook, or guidance that conflicts
with — or fails to make explicit — anything above is corrected at its owner
immediately, this session, never deferred. Every session revalidates governance
against these directives. Reinforce and revalidate with the project's advanced
verification tooling (WAZA via the Make dispatcher) plus DRY/SSOT/YAGNI
methods. Rules/config changes flow SSOT → generator → projections. Experience
gained in a session lands as improved skills/commands/rules/docs/ADRs in the
same cycle. A rule or strategy change in code/docs without operator
authorization is a severe violation; the NEWEST correct rule wins, and when
hierarchy cannot be determined, stop and ask.

## 10. Closure — the full cycle or nothing

Done = full scope + green gates (fix, fmt, check, test) + WAZA + zero residue +
complete gitflow: scoped commit → fast-forward push → PR → review resolved →
`--no-ff` merge into the DECLARED integration branch → affected gates rerun on
the merged SHA → runtime proved on the integrated state → release → deploy →
activation, each with its own distinct evidence. Local green, open PR, or
"mergeable" is never landed. Stop only for a genuinely destructive action or
authority conflict — one precise question — then continue to full completion.

## Cadence and automation

- Nothing waits more than 1 minute without feedback: slow gates are defects
  fixed at their owner (cache, parallelism, scope), never endured.
- Heavy mechanical change uses ast-grep search/replace, LSP refactor, and
  code-graph discovery (crg) — never manual wiring edits.
- Lightweight discovery/verification tasks go to subagents; the coordinating
  thread keeps integration, final QA approval, and publication only.
- Coordinate online with other agents (board/beads messages), adopt their
  landed work fast, and keep beads/docs/ADRs/skills current with reality.
- Every defensible improvement to these rules lands back here in the same
  session (self-repair), with the regeneration/provenance header intact.
