---
name: make-check
description: "native gates, root make verbs, runtime-first validation"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","usage:router"]'
  version: 2.4.0
---

# Make Check

Activate when selecting or executing a repository's validation workflow. Do not start
provisioning for an ordinary writing request.

1. Read the authorized scope, repository instructions and root Makefile. Resolve the
   existing environment and command owners before invoking an operation.
2. Use `make setup` when the selected physical environment is absent or its native
   provenance check requires reconciliation. Reuse a valid environment; do not
   reinstall it before every gate. Setup consumes declared locks; upgrades use their
   separate owner.
3. Exercise changed behavior through its public runtime, then select the required
   native check and test verbs.
4. Apply bundle rule `workflow/canonical-commands` for command deadlines, profiling,
   failure outcomes and test selection. Gate placement follows
   `workflow/gate-budget`. Resolve both under the bundle's canonical `rules/`.
5. Record command, cwd, exit, decisive output, scope and cache accounting. A focused
   result proves only its named scope.

## Generation and source stability

For changed generation inputs, use the repository's declared fixed-point proof and
retain the exact source and artifact identities. A divergent second generation is a
producer defect. Coordinate a stable input window, correct its owner within the
authorized scope and rerun the invalidated proof. Do not kill another actor's lock
owner, remove its lock or restore an older tree.

## Structural work

Compose `$crg` when the selected host provides graph analysis and the change needs
structural impact evidence. The repository's domain router owns its codemod and
generation sequence. Graph candidates do not establish dead code without consumer
verification.

An excluded code repair does not become authorized because a documentation gate exposes
it. Preserve the failure, finish independent authorized corrections and report source,
integration and installed delivery separately.
