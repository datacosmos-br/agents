---
globs: ["*.py", "**/*.py"]
---
# Python Rules — STRICT (Pydantic 2 + Python 3.13 + AGENTS.md SSOT/MRO/YAGNI)

> ⛔ **LEI SUPREMA — RESOLVER, NUNCA ESCONDER (NO-BYPASS / ROOT-CAUSE-ONLY).** Prevalece sobre toda
> regra deste arquivo. Defeito corrige-se na RAIZ e verifica-se verde — nunca mascarado (`except: pass`,
> `IFERROR`-para-default, fallback silencioso, valor inventado), silenciado, contornado ou reportado
> verde sem verificação. Detalhamento: §5d. Canônico: `~/.claude/AGENTS.md` §0.

These rules are **inviolable** for every `.py` file. Loaded automatically for any task that touches Python.

## 0. Validation is GLOBAL (mandatory — AGENTS.md §3.8)

After **any** Python edit, validate the **entire workspace**, not only the touched file:

- `make lint` (or `ruff check . --fix --unsafe-fixes` + `ruff format .`) — zero findings.
- `make typecheck` (or `pyrefly check`) — zero errors.
- `make test` — all green.
- LSP diagnostics on every edited `.py` — zero.
- `wc -l` per touched module — must be **< 200 logical LOC** (AGENTS.md §3.1).

Fix every finding at its **source**. Never suppress. If any gate is red, work continues — claims of "done" require timestamped green output.

## 1. Forbidden typing constructs

The following are **forbidden**. Every occurrence is a defect:

- `Any` / `typing.Any` / `cast(Any, …)` — replace with the precise type, a `TypeVar` with `bound=`, a `Protocol`, or a discriminated union.
- `object` as a type annotation — signals a missing model. Replace with the actual contract.
- Bare `types` module use for ad-hoc shapes (`types.SimpleNamespace`, raw `TypedDict`, …) — use Pydantic 2 models.
- `# type: ignore` — fix the type at its source. The **only** acceptable exception is a narrow third-party stub gap, and it MUST carry a code (`# type: ignore[<code>]`) plus a `Why:` comment with the reason.
- `# noqa` without a specific code (`# noqa: <code>`) and a `Why:` comment.
- `bare except:` — always specify the exception class.
- `Optional[X]` / `Union[X, Y]` / `List[X]` / `Dict[K, V]` / `Tuple[…]` / `Set[X]` from `typing` — use `X | None`, `X | Y`, `list[X]`, `dict[K, V]`, `tuple[…]`, `set[X]` (Python 3.9+; mandatory under 3.13).
- `os.path.*` — use `pathlib.Path`.
- `bool` / `None` returns to signal failure — use `r[T]` (AGENTS.md §3.3).
- Loose module-level constants (`str`, `tuple[str, …]`, `dict[str, str]`, list-of-strings) — use `enum.StrEnum`, `frozenset[StrEnum]`, `types.MappingProxyType[StrEnum, T]`, or a Pydantic 2 `m.FrozenModel` / discriminated `m.<Domain>.<Mapping>`. Compose into a `Flext*Constants` facade via MRO mixins (AGENTS.md §3.1).

## 2. Pydantic 2 way only

- Use `model_config = ConfigDict(...)`, `Field`, `model_validator`, `field_validator`, `RootModel`, `computed_field`, discriminated unions via `Field(discriminator=...)`.
- **Forbidden v1 forms** (every occurrence is a defect): `class Config:`, `@validator`, `@root_validator`, `parse_obj`, `parse_raw`, `.dict()`, `.json()`, `__fields__`, `update_forward_refs`, `Field(allow_mutation=…)`, `Config.allow_population_by_field_name`.
- v2 equivalents: `model_validate`, `model_validate_json`, `model_dump`, `model_dump_json`, `model_fields`, `model_rebuild`, `model_config = ConfigDict(populate_by_name=True)`.

## 3. Python 3.13 syntax

- `from __future__ import annotations` at the top of every module.
- Built-in generics (`list[…]`, `dict[…]`, `set[…]`, `tuple[…]`).
- `X | Y` over `Union`; `X | None` over `Optional`.
- PEP 695 `type Alias = …` and generic syntax (`def f[T](x: T) -> T:`) where it clarifies.
- `match` / `case` over `if/elif` chains for type-discriminated branching.
- `asyncio.TaskGroup` over manual gather for structured concurrency.

## 4. SOLID / DRY / YAGNI

- **SRP / OCP / LSP / ISP / DIP**: respect every one. `isinstance` switching where polymorphism applies = defect. Fat protocols = defect.
- **DRY**: copy-paste with slight variation must be unified via shared abstraction or MRO mixin.
- **YAGNI**: speculative parameters, unused branches, "future hooks", abstractions with one implementation, feature flags for non-existent features → **delete**.
- **Parameter sprawl** (> ~4 parameters) → restructure into a Pydantic 2 model or split the function.
- **Stringly-typed code** (raw strings where `StrEnum` / discriminated unions exist) → defect.
- **Nested conditionals 3+ levels** → flatten via early returns, guard clauses, lookup tables, or strategy pattern.
- **Comments**: explain only non-obvious WHY (hidden constraint, subtle invariant, workaround). Comments narrating WHAT or referencing the task/caller → delete.

## 5. AGENTS.md SSOT / MRO (FLEXT)

- **Search-first, write-last**: before writing any new function/class/module, `Grep` / `ast-grep` for an existing primitive in `flext-core` → `flext-cli` → `flext-infra` → `flext-tests` → consumers.
- **No new wrappers / helpers / proxies / aliases / standalone functions** (§3.5). Compatibility shims forbidden.
- **MRO mandatory** wherever it deduplicates (§2.3). Standalone classes that share concerns → Mixins composed into the top-level `Flext*` facade.
- **Library abstraction** (§2.7): pydantic, dependency_injector, structlog, rich, rope, … flow through their owning project's contracts (`m.*`, `c.*`, `t.*`, `u.*`, `p.*`). Direct `from <lib> import …` outside the abstraction owner → defect.
- **Cross-project propagation**: when a primitive is centralized, propagate the deletion of every duplicate workspace-wide via `ast-grep` chain-of-use in the **same** iteration.
- **Net LOC must be negative** for every refactor / cleanup / simplify run.

## 5a. Protocol-first design (mandatory)

Protocols are the contract. Concrete classes are implementations.

- **Type parameters and return types with protocols** from `p.*` whenever one exists. Never type a parameter as a concrete `Flext*` class when the corresponding `p.<Name>` protocol exists — depend on the contract, not the implementation (DIP).
- **If a needed method is missing from the protocol** the caller depends on, **update the protocol** (and its docstring) in the same iteration. Don't duck-type around a missing protocol method, and don't downcast to the concrete class — that's a leaky abstraction.
- **If a recurring usage pattern emerges across multiple call sites**, surface it on the protocol itself (a default-method, a `@runtime_checkable` extension, or a sibling protocol composed via MRO). Never let callers re-implement the same shape against a too-thin protocol.
- **Cross-project**: when you tighten a `p.*` protocol, propagate updates to every implementer in the same iteration via `ast-grep` (AGENTS.md §3.5 Integral Changes).
- **Generic protocols**: prefer PEP 695 generic syntax (`class Repo[T](Protocol): ...`) over `Generic[T]` + `TypeVar`.
- **`@runtime_checkable`** only when actually used at runtime. Don't decorate speculatively.

## 5b. Centralized-helper ergonomics (DRY at the *helper* level)

When the same pattern shows up in 2+ places and each call site does **a lot of work** to use the helper, the bug is in the helper, not the callers.

- **Push complexity into the helper**, not into every caller. If `f()` returns a value that 5 call sites all post-process the same way, return the post-processed value from `f()`.
- **Direct delivery**: helpers should hand callers the value they actually use, not a low-level intermediate that needs unwrapping, parsing, or branching at each call site.
- **Ergonomic surface**: prefer `helper.do(x, **opts)` returning `r[Result]` ready for chaining over a triplet `helper.prepare`/`helper.execute`/`helper.finalize` that every caller has to wire together.
- **Compose, don't expand**: if a helper grows N parameters to support M call-site variants, replace the parameters with a Pydantic 2 spec model (`m.<Name>Spec`) and add named factory classmethods (`Spec.for_<variant>(...)`).
- **Update the helper, not the callers**: when refactoring repeated logic, modify the centralized helper in `flext-core` / `flext-cli` / `flext-infra` / `flext-tests` and propagate deletions of the now-redundant call-site logic in the **same** iteration.

## 5c. `FlextResult` / `FlextExceptions` DSL — mandatory mnemonics

Reduce LOC drastically by using the high-level combinators instead of imperative branching. Treat `r[T]` as a monadic value — chain, don't unwrap-and-rebuild.

**Forbidden imperative pattern**:

```python
res = do_something(x)
if not res.is_success:
    return FlextResult.fail(res.error)
val = res.value
res2 = do_more(val)
if not res2.is_success:
    return FlextResult.fail(res2.error)
return FlextResult.ok(transform(res2.value))
```

**Required combinator form**:

```python
return do_something(x).flat_map(do_more).map(transform)
```

DSL mnemonics (use the canonical name from your `flext-core` `r`/`FlextResult` API; aliases vary slightly per release — check `r.__all__` or `c.Result.METHODS`):

| Pattern at call site | Combinator (replaces it) |
|---|---|
| `if r.is_success: x = f(r.value); return ok(x)` | `r.map(f)` |
| Chain a fallible call | `r.flat_map(g)` / `r.bind(g)` / `r.and_then(g)` |
| Default on failure | `r.unwrap_or(default)` / `r.value_or(default)` |
| Recover with another `r[T]` | `r.or_else(handler)` |
| Branch on success/failure | `r.match(ok=..., err=...)` |
| Wrap a raising callable | `FlextResult.try_(fn, *args, **kw)` / `r.from_callable(fn)` |
| Combine many results | `FlextResult.gather(*rs)` / `FlextResult.sequence(rs)` |
| `None` → `r[T]` | `FlextResult.from_optional(x, err=...)` |
| Discard error context | (forbidden) — always preserve via `.map_err(...)` |
| Side-effect on success/failure | `r.tap(f)` / `r.tap_err(f)` |

**Exceptions** (`FlextExceptions` family in `flext-core`):

- **Always raise from the family** — never raise bare `Exception`, `ValueError`, `RuntimeError`, etc., when a `FlextExceptions.<Specific>` already covers the case (`NotFound`, `Conflict`, `ValidationError`, `Unauthorized`, `Timeout`, …).
- **Bridge to `r[T]`**: never `try: ... except: return FlextResult.fail(str(e))`. Use `FlextResult.try_(...)` (or the project's equivalent decorator) so the exception is captured *and typed* by the family.
- **`raise … from exc`** is mandatory whenever you re-raise — preserve the chain.
- **Add a new exception class to the family** (and update the protocol that consumes it) instead of stuffing context into a string message at every call site.
- **Mnemonics**: prefer the named factory classmethods (`FlextExceptions.NotFound.for_(entity, key=...)`, `FlextExceptions.Conflict.between(a, b)`, …) so exception construction is one line everywhere.

When in doubt: if your function body has more than one `if r.is_success` or `if not r.is_success` branch, you are doing it wrong — refactor with the combinators above.

## 5d. Minimize exceptions; propagate errors honestly

The codebase must be **productive and resilient — without hidden failures.** Exceptions are a last resort; `r[T]` is the default error channel.

### Reduce raises to the minimum

- **Prefer `r[T]` over raising.** Any operation that can fail under business conditions returns `r[T]`. Reserve `raise` for genuinely exceptional, non-recoverable invariants (programmer errors, corrupt state, contract violations) and for the **outermost adapter** that translates `r[T]` into HTTP/CLI/RPC responses.
- **Don't raise inside pure domain logic.** Validation failures, "not found", "conflict", "unauthorized", etc. are **values**, not exceptions — return `r.fail(FlextExceptions.NotFound.for_(...))`.
- **Don't `try/except` around control flow.** EAFP-as-control-flow inside business logic is a defect — express the branch with `r[T]` combinators.
- **One try-boundary per integration.** When you must call into a library that raises (DB driver, HTTP client, file system), wrap the call **once** at the boundary with `FlextResult.try_(...)` (or the project's adapter) and return `r[T]` from there onward.

### No bypass · No hiding · No invention

These anti-patterns are **forbidden**. Every occurrence is a defect:

| Anti-pattern | Why it's a defect | Required form |
|---|---|---|
| `try: ... except: pass` | Bypass — silently drops failures | `r.tap_err(log)` then return / propagate the failure |
| `try: ... except: return None` | Hides failure as an indistinguishable value | Return `r[T]` and let caller decide |
| `try: ... except: return default` | Invents data; caller cannot tell real-vs-fallback | Return `r[T]`; if a default is genuinely meaningful, expose it via `r.unwrap_or(default)` at the **caller**, not inside the producer |
| `try: ... except: logger.error(...); continue` | Loses structured error, hides skipped items | Collect failures via `FlextResult.gather` / `partition` and return them |
| `if x is None: return ...` after a fallible call | Fallback masquerading as success | Producer must return `r[T]`; never return `None` for "missing" |
| Catching `Exception` broadly | Loses specificity; silences bugs | Catch the specific exception class and translate to the corresponding `FlextExceptions.<Specific>` |
| `except SomeError: raise OtherError(...)` (no `from`) | Loses chain — debuggability collapses | `raise OtherError(...) from exc` always |
| Returning a "partial success" sentinel value | Mixes channels; callers re-implement detection | Return `r[T]` with a structured error payload |

### Layer-correct propagation

Errors must travel up **with their semantics intact** — no laundering, no demotion.

- **Domain errors stay domain errors.** A `FlextExceptions.ValidationError` raised in the model layer must surface to the caller *as* a `ValidationError`, not as a generic `RuntimeError` swallowed by the service layer.
- **Adapt at boundaries, don't repackage internally.** Translation only happens at well-defined seams: infra → domain (e.g., `IntegrityError` → `FlextExceptions.Conflict`), domain → transport (e.g., `NotFound` → HTTP 404). Inside a layer, propagate unchanged.
- **No silent demotion.** Never convert a structured `FlextExceptions.<Specific>` into a string (`r.fail(str(exc))`) — preserve the exception object so the next layer can pattern-match.
- **No `try/except/raise generic`.** Wrapping the original error in a less-specific one is a defect. Either propagate as-is, or translate to a *more*-specific class with `from exc`.
- **Surface batched failures honestly.** When processing N items, don't return only the successes. Return both via `FlextResult.partition(rs)` (or equivalent) so the caller sees what failed and why.

### Resilience ≠ silence

- **Retries**, **circuit breakers**, **timeouts**, and **fallbacks** are valid resilience mechanisms — but each must be **explicit and observable**:
  - Use the `r[T]` retry combinator (or the project's `Resilience` mixin); never wrap in `while True: try/except`.
  - Every fallback must be logged structurally and exposed in the result metadata so the caller knows a fallback happened.
  - A retried-and-still-failing call returns `r.fail(...)` — it does not invent a success.
- **Idempotency keys, dedup, and graceful degradation** are features, not exception-eating. Implement them with explicit `r[T]` flow, not by catching and ignoring.

### Productivity through directness

- The shortest correct code uses combinators end-to-end: producer returns `r[T]`, intermediates `flat_map` / `map`, the boundary `match(ok=..., err=...)` once.
- If your function body has *any* `try/except` that isn't the single boundary translation, refactor.
- If your function body has any branch on `None` after calling another internal function, the other function's signature is wrong — make it return `r[T]`.

## 6. Tooling

- Always `make lint` / `make typecheck` / `make format` / `make test` (project Makefile is the single entry point).
- Use `ast-grep` (`sg`) for structural search and rewrite, not regex.
- Use Serena / Scope / LSP for navigation; never read whole source files when symbolic tools suffice.

## 7. References

- AGENTS.md §3.1 SUPREME LAW (200-LOC, no loose functions, constants-first)
- AGENTS.md §2.3 MRO Composition
- AGENTS.md §2.7 Library Abstraction
- AGENTS.md §3.3 Result Types (`r[T]`)
- AGENTS.md §3.5 Legacy Extermination (no wrappers, integral cross-project deletion)
- AGENTS.md §3.8 Verification (timestamped evidence)
- `skills/simplify/SKILL.md` — generic behavior-preserving simplification workflow
