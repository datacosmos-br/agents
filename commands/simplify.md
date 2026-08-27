---
name: simplify
description: Simplify specified code via STRICT AGENTS.md / SOLID / DRY / YAGNI rules — collapse modules to <200 LOC, maximize reuse, no `Any`/`object`/`# type: ignore`, Pydantic 2 + Python 3.13. Always validate and fix all pyrefly + ruff failures globally.
argument-hint: "<file paths, function names, or code description>"
---

# Simplify: STRICT Code Simplification

Simplify the **explicitly specified** code. Reduce modules to **< 200 logical LOC** by maximizing reuse of existing primitives and following AGENTS.md SSOT/MRO/YAGNI rules. Always validate and fix **all** pyrefly + ruff failures **globally** (workspace-wide), not just on touched files.

## Phase 1: Identify Target Code (NEVER use git)

The user specifies what to simplify via: `$ARGUMENTS`

- **If arguments are provided**: Read those files / functions / modules. They are the review targets.
- **If no arguments are provided**: Ask the user which files or code sections to simplify. Stop. Do NOT fall back to git, do NOT use `git diff`, do NOT scan recent edits, do NOT infer scope. Scope is **always explicit**.

Read the full content of the target files before launching agents — agents need the complete code, not summaries.

## Phase 2: Launch Four Review Agents in Parallel

Use the Agent tool to launch all four agents concurrently in **a single message**. Pass each agent the full code content and the relevant rules from this skill.

### Agent 1: Reuse + LOC Reduction (AGENTS.md SSOT/MRO)

Goal: collapse modules, delete duplication, route everything through existing facades.

1. **Search-first, write-last.** Before suggesting any new code, run `Grep` / `ast-grep` for existing primitives that already cover the concern. For FLEXT projects search in this order: `flext-core` → `flext-cli` → `flext-infra` → `flext-tests` → consumers.
2. **Module size cap (AGENTS.md §3.1 SUPREME LAW): ≤ 200 logical LOC.** Any file over 200 LOC is a violation. Propose splits **via OO decomposition / MRO mixins**, never via line-removal hacks or by extracting throwaway helper modules.
3. **No new wrappers / helpers / proxies / aliases / standalone functions** (AGENTS.md §3.5). Compatibility shims (`def old(): return new()`) are forbidden — delete and replace at all call sites in the same iteration.
4. **MRO mandatory wherever it deduplicates** (AGENTS.md §2.3). Standalone classes that share concerns must become Mixins composed into the top-level `Flext*` facade. A facade MUST strictly compose ALL of its domain-specific subclasses.
5. **Cross-project propagation.** When a primitive is centralized, propagate the deletion of every duplicate workspace-wide via `ast-grep` chain-of-use in the SAME iteration (§3.5 Integral Changes).
6. **Library abstraction (§2.7).** External libs (pydantic, dependency_injector, structlog, rich, rope, …) MUST flow through their owning project's contracts (`m.*`, `c.*`, `t.*`, `u.*`, `p.*`). Flag any direct `from <lib> import …` outside the abstraction owner.
7. **Constants-first (§3.1).** Loose module-level `str` / `tuple[str, …]` / `dict[str, str]` / list-of-strings are FORBIDDEN. Replace with the most-restrictive Pydantic 2 / Python 3.13 form:
   - enumerable strings → `enum.StrEnum` (or `c.<Domain>.<Enum>`)
   - immutable membership → `frozenset[StrEnum]`
   - immutable lookup → `types.MappingProxyType[StrEnum, T]` or `m.FrozenModel`
   - typed key→value → discriminated `m.<Domain>.<Mapping>` Pydantic 2 model
   Constants compose via `FlextConstants` (or `FlextInfraConstants`, …) facade through MRO mixins per domain. Sub-domain constants live as nested classes; never flat module-level attributes.

Output: a deletion list (LOC removed, files collapsed, duplicates eliminated) and the canonical primitive each call site should resolve to.

### Agent 2: Quality — SOLID / DRY / YAGNI / Typing Strictness

Review the same code for hacky patterns and STRICT typing violations.

**SOLID / DRY / YAGNI:**
1. **SRP violations:** modules / classes mixing concerns — split by responsibility into MRO mixins under one facade.
2. **OCP / LSP violations:** type-checks (`isinstance`) where polymorphism applies; subclasses that break parent contracts.
3. **ISP violations:** fat protocols / ABCs forcing consumers to depend on methods they don't use — split protocols.
4. **DIP violations:** high-level modules importing concrete low-level classes — depend on the contract (`p.*` / `t.*`) instead.
5. **DRY violations:** copy-paste with slight variation — unify via shared abstraction or MRO mixin.
6. **YAGNI violations:** speculative parameters, unused branches, "future hooks", abstractions with one implementation, feature flags for non-existent features. **Delete.**
7. **Parameter sprawl:** > ~4 parameters → restructure into a Pydantic 2 model or split the function.
8. **Stringly-typed code:** raw strings where `StrEnum` / branded types / Pydantic discriminated unions exist — replace.
9. **Nested conditionals 3+ levels:** flatten via early returns, guard clauses, lookup tables, or strategy pattern.
10. **Redundant state:** state duplicating other state, cached values that could be derived, observers/effects that could be direct calls.
11. **Leaky abstractions:** internal details escaping module / package boundaries.
12. **Unnecessary comments:** comments explaining WHAT well-named identifiers already say, change-narration, task references — delete; keep only non-obvious WHY (hidden constraint, subtle invariant, workaround).

**STRICT TYPING (Python 3.13 + Pydantic 2):**
13. **`Any` is FORBIDDEN.** Replace with the precise type, a `TypeVar` with bound, a `Protocol`, or a discriminated union. No `typing.Any`, no `cast(Any, …)`, no `# type: ignore` swallowing.
14. **`object` is FORBIDDEN as a type annotation.** It signals a missing model. Replace with the actual contract.
15. **Bare `types` module use is FORBIDDEN** for ad-hoc shapes (e.g. `types.SimpleNamespace`, untyped `TypedDict` from `types`, …). Use Pydantic 2 models.
16. **`# type: ignore` is FORBIDDEN.** Fix the type at its source. The only acceptable exception is a narrow third-party stub gap, and it MUST carry a code (`# type: ignore[<code>]`) plus a `Why:` comment — flag every other use.
17. **Pydantic 2 way only:** `model_config`, `Field`, `model_validator`, `field_validator`, computed fields, `RootModel`, discriminated unions via `Field(discriminator=...)`. Flag any v1 syntax (`Config` class, `validator`, `root_validator`, `parse_obj`, `dict()`, `.json()`).
18. **Python 3.13 syntax:** built-in generics (`list[…]`, `dict[…]`, `set[…]`); `X | Y` over `Union`; `X | None` over `Optional`; `from __future__ import annotations` at top; PEP 695 `type` aliases and generic syntax where it clarifies. Flag legacy forms.
19. **Result types:** `r[T]` for fallible operations (AGENTS.md §3.3). Flag `bool` / `None` returns used to signal failure.
20. **`bare except:`** is FORBIDDEN — always specify the exception class.
21. **`pathlib.Path`** over `os.path` everywhere.

### Agent 3: Efficiency

Review the same code for efficiency:

1. **Unnecessary work:** redundant computations, repeated file reads, duplicate API calls, N+1 patterns.
2. **Missed concurrency:** independent operations sequential when they could be parallel (`asyncio.gather`, `TaskGroup`).
3. **Hot-path bloat:** blocking work on startup or per-request / per-render hot paths.
4. **Recurring no-op updates:** state writes inside loops / handlers that fire unconditionally — add change-detection guards. Verify wrapper functions taking updater callbacks honor same-reference / "no change" signals.
5. **Unnecessary existence checks:** pre-checking file/resource existence before operating (TOCTOU) — operate directly, handle the error.
6. **Memory:** unbounded structures, missing cleanup, listener leaks, generators consumed twice.
7. **Overly broad operations:** reading whole files when slices suffice; loading entire collections to filter for one.

### Agent 4: Protocol-First + Helper Ergonomics + FlextResult/FlextExceptions DSL

Goal: raise the abstraction level — push complexity into protocols and centralized helpers; collapse imperative branching into combinator chains. Drastic LOC reduction is the metric.

Apply the rules from `~/.agents/rules/python.md` §5a (Protocol-first design), §5b (Centralized-helper ergonomics), §5c (`FlextResult` / `FlextExceptions` DSL with mnemonic table), and §5d (Minimize exceptions; propagate errors honestly — no bypass / no hiding / no invention).

Output a list of:
- `isinstance` downcasts to update on the relevant `p.<Name>` protocol;
- helper signatures to redesign for direct-result ergonomics (Pydantic 2 spec model + factory classmethods);
- imperative `is_success` / `is_failure` chains to collapse into `map` / `flat_map` / `or_else` / `match` / `partition`;
- bare raises to translate into `FlextExceptions.<Specific>` named factories;
- bypass / hiding / invention patterns (`except: pass`, `except: return None|default`, broad `Exception`, `r.fail(str(exc))`, `while True: try/except`) to replace with typed `r[T]` propagation.

## Phase 3: Fix Issues

Wait for all four agents to complete. Aggregate findings and fix each issue **directly** in the target files. False positives: skip silently, don't argue.

## Phase 4: GLOBAL Validation (mandatory — AGENTS.md §3.8)

Validation is **non-negotiable** and **workspace-wide**. After fixes, run the gates against the **entire workspace**, not only the touched files. Every claim of "done" requires fresh timestamped command + output.

Required gates (run all, fix all failures, re-run until clean):

1. **Ruff (lint + format) — global:**
   - `make lint` (preferred) or `ruff check . --fix --unsafe-fixes`
   - `make format` or `ruff format .`
   - Resolve every `E*`, `F*`, `B*`, `I*`, `UP*`, `RUF*`, `SIM*`, `PL*`, `PT*` finding. No `# noqa` without a `Why:` and a specific code.
2. **Pyrefly (typecheck) — global:**
   - `make typecheck` (preferred) or `pyrefly check`
   - Zero errors. **No `# type: ignore`** to silence pyrefly. Fix the type at its source.
3. **Pytest:** `make test` — all pass.
4. **LSP diagnostics:** zero on every edited `.py`.
5. **Module size:** `wc -l` per touched module to confirm < 200 logical LOC.

If any gate fails, fix the failure (fix the root cause — never suppress) and re-run. **All gates must be green over the whole workspace before declaring done.**

**Net LOC must be negative.** Every simplify run should DELETE more than it adds. If LOC went up, stop and request user authorization with a written reason.

When done, summarize: files collapsed, LOC delta (must be negative), duplicates removed, primitives reused, and the green output (with timestamps) of the global lint/typecheck/test runs.
