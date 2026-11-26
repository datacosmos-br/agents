---
name: gov-automation-cycle
description:
  Run a FLEXT program slice through the canonical mod→check→runtime→tests→crg-evidence→landing
  cycle.
metadata:
  aihub.tags: '["decision:ADR-0020","effective:2026-09-11","route:project"]'
---

# FLEXT Program Automation Cycle

Execute one bead slice end-to-end without ad-hoc tool invocations. Gate contract: the
`flext-gates-as-products` skill; rule authoring: the `codemod` skill. Placement follows
`rules/git/gitflow-branch-pr.md`, the environment `rules/storage.md`.

```bash
# 0. Authorized-context preflight (actual runtime root, pins fresh)
export UV_PROJECT_ENVIRONMENT=$PWD/.venv VIRTUAL_ENV=$PWD/.venv

# 1. A full structural rewrite runs only when ordered (ast-grep catalog, text
#    rules, fixed point). New or widened rules: codemod skill.
make mod

# 2. The delivery cycle (rules/workflow/agent-delivery-doctrine.md): the only gate,
#    then the runtime proof, then the test verb last.
make check
make tests

# 3. Graph evidence (agent-side tool only; operate per the crg skill:
#    freshness gate first, lane graph, verified verbs)
code-review-graph doctor --repo "$PWD"                        # health checklist
code-review-graph update --brief --repo "$PWD"                # per commit (build if it exits 1)
code-review-graph detect-changes --brief --repo "$PWD"        # PR evidence
code-review-graph dead-code --json --repo "$PWD"              # R2 residue candidates
code-review-graph impact --repo "$PWD"                        # blast radius

# 4. Scoped commit (hook gates) → merge --no-ff of the integration tip → push →
#    PR → green CI merge → graph refresh on the tip (crg runbook).
```

Graph operation, limits, and the manual runbook: `~/.agents/skills/tool/crg/SKILL.md`.

Rules that may fire are the engine's packaged catalogs in flext-infra:
- ast-grep rules under `src/flext_infra/config/rules/ast-grep/`;
- text rules in `src/flext_infra/config/rules/mod/sed.yaml`;
- each repository's own overlay under `config/rules/`.

The workspace guide `docs/guides/codemod-rules.md` documents the schema and verbs. Never
hand-invent rule sources or bypass the verbs with raw commands.
