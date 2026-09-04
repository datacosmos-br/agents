---
description: Publishing work — creating a branch, commit, push, or opening a PR. Load when the user asks to commit, push, land, publish, open a pull request, or before any git push.
---

# Branch and PR — parameterized GitFlow (ADR-0016)

Work only on `feature/<slug>`, `bugfix/<slug>`, `hotfix/<slug>`, or
`release/<version>` via `gc sling` — never on the checkout of `main` or the
integration base. Forbidden lane prefixes: `epic/`, `cycle/`, `agent/`, `wip/`.

- Lifecycle owner: gascity `gc sling` / `gc hook` / `gt done` / `gc convoy`.
  AI Hub does not create worktrees or branches and does not open pull requests.
- Integration base = project `config/workspace.yaml` → `integration.branch`
  (ai-hub: `dev`). Never invent `develop`.
- One git root per PR; never mix two repositories in one commit or PR.
- **Commit and push:** stage bead-scoped paths, commit, FF push. Let
  pre-commit/pre-push/CI validate — do not re-run the full gate matrix by hand
  before every commit (`UNIVERSAL_CORE` Law 7).
- Land opens/updates the PR; merge into the integration base with `--no-ff`;
  revalidate on the base; then `gt done`.
- Promotion to `main` waits for explicit operator approval.

Detail and receipts: `docs/worktrees.md`, ADR-0016. Do not duplicate here.
