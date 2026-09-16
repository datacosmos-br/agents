# Lane scenario — superproject worktree after an integration merge

- Checkout: a linked worktree of a superproject with 30 git submodules, on a
  lane branch that just merged the integration tip (member gitlinks moved).
- `code-review-graph doctor --repo "$PWD"` reports `graph: no nodes` (critical).
- A tracked Gemini hook script in the checkout runs
  `code-review-graph update --skip-flows --repo "<primary checkout path>"`.
- The operator wants to rename the class `FlextConfigLoader` to
  `FlextConfigSource` across the superproject and its members, and to know the
  blast radius before any edit. The repository owns a codemod verb
  (`make mod`) that applies rewrites.
