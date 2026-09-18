# Result operation guide

## Authority and decision

Use the project's public `r` facade for construction and `p.Result[T]` for contracts.
`flext_core.result` declares `r = FlextResult`; it is not a separate wrapper. Inspect
`flext_core/result.py`, `_result/*.py`, and `_protocols/result.py` in the selected
dependency and branch-matched source. Private modules are research evidence, never
consumer imports.

The source and ai_hub installed dependency inspected on 2026-09-17 agree on the
operations below. This is a source observation, not runtime test evidence or a promise
about another installed version. Context7 has no matching flext-core reference; local
authoritative implementation and protocol govern. If they diverge, resolve the
dependency owner before choosing syntax.

For the one requested call site, establish input/output types, failure fields, which
exceptions must escape, callback invocation count/order, and existing effects. Prefer
`return existing_result` when the signature already matches. Only then consider one
mnemonic operation. A shorter expression is not a correctness argument. Do not introduce
helpers, wrappers, aliases, long lambda chains, dependency changes, or a repo-wide
railway rewrite. Reuse existing named operations; ordinary branches remain the simplest
choice when contracts differ.

## Mnemonic table

| Form                                                              | Remember                    | Exact selection constraint                                                                                                                         |
| ----------------------------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `r[T].ok(value)`                                                  | Start success               | Carries a real T; `None` and bare `object()` success payloads are rejected.                                                                        |
| `r[T].fail(error, error_code=..., error_data=..., exception=...)` | Start failure               | Creates a domain failure; metadata is validated/redacted by the owner. Not permission to catch raw exceptions.                                     |
| `result.map(operation)`                                           | T -> U                      | Callback returns a value, not a Result; skips failed input and propagates its failure fields.                                                      |
| `result.flat_map(operation)`                                      | T -> Result[U]              | Callback returns `p.Result[U]`; copies into the concrete result family rather than nesting. Does not promise Result object identity.               |
| `result.flow_through(first, second)`                              | T -> Result[T], repeatedly  | Each callback consumes the previous success of the same payload type; stops on failure. Not a heterogeneous chain or transaction.                  |
| `result.tap(observer)`                                            | T -> None, keep T           | Success-only side effect; returns the original result if observer completes. Observer failure can replace success; not infallible logging.         |
| `result.fold(on_failure, on_success)`                             | Result[T] -> U              | Explicit exit boundary; exactly one callback runs. Failure callback receives error text only, not code/data/exception. Callback exceptions escape. |
| `r[U].from_failure(source)`                                       | Carry failure across T -> U | Requires failed source; forwards error, code, data, exception through `fail`. Success input raises `ValueError`.                                   |

`from_failure` retains the exception object but is not a raw rethrow or a byte-for-byte
arbitrary metadata copy: `fail` applies canonical validation, sensitive-key redaction,
and exception-derived fields; empty error text is normalized to `""`. Prefer a direct
return for identity and exact existing state. Never replace it with
`r[U].fail(source.error)` when code/data/exception matter.

No `bind`, `>>`, or `and_then` alias is declared by this API. Do not borrow operators
from another railway library. `map` with a Result-returning callback creates a nested
payload; use `flat_map` only after checking the contracts.

## Exception and effect guard

Current `map`, `flat_map`, `flow_through`, and `tap` catch `c.EXC_BROAD_RUNTIME`:
`ArithmeticError`, `AttributeError`, `KeyError`, `RuntimeError`, `TypeError`, and
`ValueError`. They produce failed Results with `str(exc)` and `exception=exc`. This is
catch-based conversion, not raw exception propagation. The set does not include
`OSError` or `ImportError`; inspect the actual constant, never say all exceptions are
caught.

Do not introduce these operations across a boundary requiring the first raw exception
and traceback unchanged. Use them only when callbacks are proven total over the accepted
domain or the existing selected boundary explicitly requires this precise Result
conversion and project policy permits it. A framework capability never overrides a
stricter project fail-fast rule.

`unwrap()` on failure raises a new `RuntimeError` using the error text. It does not
re-raise the stored exception or explicitly chain it as the cause. Appending `.unwrap()`
cannot restore raw fail-fast semantics. `.value` on failure also raises `RuntimeError`;
inspect success before extracting a value.

`unwrap_or`, `unwrap_or_else`, `map_or`, and `result | default` erase failure at
extraction. `recover` and `lash` may turn failure into success; `lash` is not a
success-path composition alias. Do not introduce them to shorten failure checks.
Likewise, `fold` is not a safe replacement when the boundary needs structured failure
metadata; use explicit branching or the existing owner instead.

Short-circuiting prevents later callbacks, not already-completed effects. `tap` can
partially perform an effect before failing; no combinator rolls it back. Preserve effect
ordering, count, and failure visibility.

## Before and after: direct return

Existing `self.store.load()` returns `p.Result[str]`; this method has the same contract
and performs no transformation or effect.

Before:

```python
def load_label(self) -> p.Result[str]:
    loaded = self.store.load()
    if loaded.is_success:  # Incorrect API spelling as well as needless wrapping.
        return r[str].ok(loaded.value)
    return r[str].fail(loaded.error)
```

After:

```python
def load_label(self) -> p.Result[str]:
    return self.store.load()
```

The direct return retains the actual result and all its failure fields. The real state
properties are `success` and `failure`, not `is_success` or `is_failure`. No identity
`map`, `tap`, helper, or redundant construction is needed.

## Before and after: change payload without discarding failure

`self.store.read_text()` returns `p.Result[str]`; this method returns the text length.
`len` on the accepted string domain is total and has no side effects.

Before:

```python
def text_size(self) -> p.Result[int]:
    loaded = self.store.read_text()
    if loaded.failure:
        return r[int].fail(loaded.error)
    return r[int].ok(len(loaded.value))
```

After:

```python
def text_size(self) -> p.Result[int]:
    return self.store.read_text().map(len)
```

This also corrects the dropped code/data/exception under the declared failure contract.
If explicit branching is required, replace only the failure line with
`return r[int].from_failure(loaded)` and keep the success branch. For an existing typed
operation returning `p.Result[int]`, choose `flat_map` instead of `map` only if its
exception and effect contract also permits it.

## Fail-fast counterexample: do not shorten this

The existing parser raises `ValueError` with its original traceback for invalid text;
the boundary requires that exception to escape, while a failed read stays a Result.
Preserve this implementation:

```python
def read_port(self) -> p.Result[int]:
    loaded = self.store.read_text()
    if loaded.failure:
        return r[int].from_failure(loaded)
    return r[int].ok(int(loaded.value))
```

Rejected rewrite: `return self.store.read_text().map(int)`. Invalid text now becomes a
failed Result instead of raising `ValueError`. Calling `.unwrap()` on that result raises
`RuntimeError`, not the original exception. Keep the explicit branch; do not add a
rethrow helper or modify the library to justify a mnemonic.

## Proof for a selected rewrite

Through the public consumer, verify success value/type, failed-input callback
non-execution, error/code/data/exception fields under canonical redaction, and callback
effects exactly once in order. Exercise the actual required exception type and traceback
boundary, not just `.failure`. Use the project's native gates from the parent skill.
Report semantic non-equivalence instead of silently relaxing policy; offline skill eval
validation alone is not live agent proof.
