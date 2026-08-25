# Engineering Practices Law

Owner of good-vs-bad engineering practice for ALL code, any language. Skills
cross-reference this file; they never restate it (DRY). Enforcement: review,
lint/type/test gates, `code-review-expert`. Violations block landing.

## Good practices — always apply

1. **SRP** — one module, one reason to change. Split when reasons multiply.
2. **OCP** — extend behavior by adding code; editing proven core needs proof.
3. **LSP** — every subtype works wherever its base is expected; no surprise
   precondition.
4. **ISP** — consumers see small role-specific interfaces, never fat ones.
5. **DIP** — high-level policy depends on abstractions; wire concrete
   implementations by constructor/parameter injection at the composition root.
6. **DRY** — one owner per fact, rule or procedure; everyone else
   cross-references the owner.
7. **YAGNI** — build exactly the current requirement; speculation is deletion
   debt.
8. **SSOT** — one authoritative source per datum; derived artifacts are
   regenerated, never hand-edited.
9. **Clean Architecture** — dependency rule points inward: entities ← use
   cases ← interface adapters; frameworks and I/O live at the edge.
10. **MRO** — inheritance graphs keep an unambiguous linearization; multiple
    inheritance cooperates via `super()` or is replaced by composition.
11. **OO discipline** — encapsulate invariants; prefer composition over
    inheritance; plain data travels in value objects.
12. **DI** — collaborators are injected at construction; business logic never
    instantiates or pins them internally.

## Bad practices — absolutely forbidden

1. **Cosmetic churn** — formatting/rename/move changes with no semantic
   finding behind them.
2. **API drift without request** — changing call signatures, endpoints or
   command surfaces without an explicit operator request naming them.
3. **Fallbacks/shims** — silent alternate paths that mask a broken primary;
   includes compat wrappers and "temporary" defaults.
4. **Hidden errors** — swallowed exceptions, suppressed warnings, red exits
   repainted green. Errors propagate or stop execution loudly.
5. **Tests above runtime** — bending runtime or tests to satisfy fixtures
   after behavior changed; runtime observation is the specification.
6. **TODO/stub residue** — placeholder bodies, unfinished branches, promised
   future work inside shipped code.
7. **Fabricated results** — inventing outputs, scores, evidence or claims not
   produced by a real executed command.
