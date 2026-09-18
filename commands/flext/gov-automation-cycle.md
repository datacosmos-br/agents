---
name: gov-automation-cycle
description:
  Run a FLEXT program slice through the canonical gen→mod→gates→crg-evidence→landing
  cycle.
metadata:
  aihub.tags: '["decision:ADR-0020","effective:2026-09-11","route:agent"]'
---

# FLEXT Program Automation Cycle

Execute one bead slice end-to-end without ad-hoc tool invocations. Full contract:
`~/.agents/skills/framework/flext-gates-as-products/SKILL.md` (§ Automation cycle).

```bash
# 0. Lane preflight (worktree must exist, pins fresh; NEVER primary venv)
export UV_PROJECT_ENVIRONMENT=$PWD/.venv VIRTUAL_ENV=$PWD/.venv

# 1. Generation first (config SSOT → projections)
make gen

# 2. Scoped semantic rewrite (ast-grep + fixed point + Ruff + Pyrefly + LSP)
#    Scope to ONE module or ONE facade slot per wave:
# make mod  (dispatch)  — or scoped:
# python -m flext_infra refactor mod --apply \
#   --module flext_core._utilities --namespace u

# 3. Hygiene + gates
make fix && make fmt && make check

# 4. Graph evidence (agent-side tool only; operate per the crg skill:
#    freshness gate first, lane graph, verified verbs)
code-review-graph doctor --repo "$PWD"                        # health checklist
code-review-graph update --brief --repo "$PWD"                # per commit (build if it exits 1)
code-review-graph detect-changes --brief --repo "$PWD"        # PR evidence
code-review-graph dead-code --json --repo "$PWD"              # R2 residue candidates
code-review-graph impact --files "$PWD" < changed... > --repo # blast radius

# 5. Scoped commit → FF push → PR → --no-ff into integration → gates on
#    merged SHA (merge --no-ff) → graph refresh on the tip (crg runbook).
```

Graph operation, limits, and the manual runbook: `~/.agents/skills/tool/crg/SKILL.md`.

Rules that may fire: anything under `flext-infra/src/flext_infra/codemod/rules/` and,
agent-globally, `~/.agents/ast-grep-rules/universal/` via `~/.agents/sgconfig.yml`.
Never hand-invent rule sources or bypass the dispatcher with raw commands.
