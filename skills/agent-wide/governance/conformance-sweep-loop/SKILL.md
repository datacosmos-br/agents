---
name: conformance-sweep-loop
description: 'conformance sweep loop, class-wave repair map, git-dep bump, declaration-first scoping'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0014","effective:2026-09-11","usage:on-demand"]'
  version: 1.0.0
---

# Conformance Sweep Loop

Personal agent workflow for driving a hosted project from any measured error
count to its declared gate threshold — repeatable, evidence-chained, and
root-cause-only. It encodes lessons that cost real debugging time on
2026-09-11 (ai-hub sweep session v2, plan
docs/plans/2026-09-11-aihub-production-sweep-plan-v2.md §1). Never project
this as project law; it composes with the project's own house rules.

## Loop (repeat N times until threshold is reached or blocked)

1. **Measure.** Run the project's canonical verification verb (typically
   `make check`) and read its structured report. One numeric baseline is the
   unit of progress for the whole loop; re-run it after every class wave.
2. **Scope first, repair second.** If a gate scans trees that are not
   production scope (tests/scripts/docs), declare the scan scope at the
   manifest SSOT BEFORE consuming the error triage — for namespace gates the
   canonical channel is manifest → conform → pyproject `[tool.<name>.<gate>]`
   → validator. Declaring scope can remove 30-50% of findings in one act
   (ai-hub 2026-09-11: namespace 1135 → 422, `make check` 2558 → 1838).
3. **Class-wave the report.** Group findings by error class, not by file.
   Pick the class with the best kill-effort ratio (see map below), work it
   to zero with the project's canonical fix verb, re-measure, and record the
   start→end numbers. Never mix two root causes in one commit.
4. **Never suppress.** A skip, a normalized catch, a blank allowlist, or a
   disabled gate is RED like a failure. The only sanctioned scope change is
   a manifest SSOT edit regenerated through the project generator, proven at
   the conformance fixed point (`<gen-verb> --mode check`-equivalent).
5. **Close the wave.** Incremental tests through the persistent selection
   cache, scoped `[WIP]`-free commit per wave when green, fast-forward push.
   Open the draft PR once, keep it open, push every wave to its same PR.

## Class-to-verb repair map (adapt keys to the project's gates)

| Finding class signature | First canonical action |
|---|---|
| test doubles / monkeypatch / mock identifiers | rewrite as typed fixture in the shared fixtures dir + public-interface call; never patch internals |
| owner-retired / compat-alias / pass-through wrapper | delete + rewire consumers to the real owner; never re-export |
| banned annotation (`dict`/`object`/`Any`/`Optional`) | replace with the project's `t.*` aliases / `p.*` protocols / `m.*` models |
| import-time wiring / module alias data | move into the facade section; compose at composition root |
| silent failure / caught exception | propagate through the Result/error family; `from_failure`, never catch→normalize |
| recursive type alias | replace with the finite alias or protocol from the project's typings facade |
| duplication clusters | one owner; all callers rewire same change |
| loc-cap / layout | nested-class decomposition or split at the composition boundary |

## External git-dependency bump rule (costly lesson — always execute)

Before pinning (or re-pinning) any `name @ git+…` dependency:

1. `git -C <dep-checkout> fetch origin <branch>` — then
   `git log --oneline <current-pin>..origin/<branch>`: if commits touching
   your failing symbol landed, the defect is already fixed upstream.
2. Install with **`--no-cache`** — uv caches built wheels for git deps and
   a fresh pin can still serve a stale cached wheel; `direct_url.json`
   records intent, not content.
3. Verify the exact surface you bumped (`'field' in Model.model_fields`)
   immediately after install, before the first generation run.
4. Determine which interpreter actually executes the dependency for the
   command at hand (workspace `.venv` vs runtime/mise python are different
   resolution roots — read the Makefile's export/override chain first).

## Incident-first ordering

When the environment is a live production runtime, order the sweep AFTER the
incident ladder: a crash-looping production daemon quantifies in restarts×CPU
 outranks any static debt. For every opened incident record the numeric
state first (`systemctl --user show <unit> -p NRestarts` and Active-since,
journald rate), then plan. If a pipeline state file (e.g. `active.json`)
gates daemon activation but the daemon does not actually consume that state,
file the decoupling ADR at its owner — never bypass the preflight.
