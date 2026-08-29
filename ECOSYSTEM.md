# ECOSYSTEM — Universal Context Patterns

How context about projects, connections, and patterns is organized across
every workspace. The living-documentation owner requires updates in the same
change that alters the pattern. Governance composes `AGENTS.md` with canonical
rules, skills, and commands through `config/governance.json`.
Role playbooks: `skills/beads-orchestrator`, `skills/beads-worker`,
`skills/governance-audit`.

## Prime Rule

Universal surfaces NEVER enumerate workspaces, projects, or their state.
Knowledge about a workspace lives IN that workspace; knowledge about how to
work lives here. Link, never copy — no project fact in universal surfaces,
no universal principle duplicated in project docs.

## The 3-Layer Context Architecture

1. **L1 — Universal law** (`~/agents`): principles and role protocols only.
2. **L2 — Role skills** (`~/agents/skills/`): how each role works, waza
   ≤500 tokens, detail in `references/` ≤1000.
3. **L3 — Workspace context** (in each workspace): how the project works —
   root `AGENTS.md`, coding standard, ADRs, project skill, ecosystem entry
   (below).

## The Workspace Ecosystem Entry (mandatory pattern)

Every workspace publishes `ECOSYSTEM.md` at its root (≤2000 tokens) with:

- **Purpose** — one paragraph: what it is, for whom.
- **Provides / Consumes** — what others may use, what it depends on.
- **Connections** — the workspaces it touches and how (library, config
  distribution, submodule, consumer, mirror).
- **Beads** — its tracker scope and current epic map (kept current).
- **Validation** — the native gate commands.
- **Pointers** — AGENTS.md, coding standard, project skill.

Agents entering a workspace read its entry first, validate key claims
against reality, and update it in the same change that alters the facts.
Auditors check entries for drift; they never centralize them.

## Global Patterns (replicate in EVERY workspace)

1. **Project knowledge base.** Root `AGENTS.md` (compact law + conventions,
   ≤2000) + full coding standard under `docs/` (≤5000) + ADRs for binding
   decisions.
2. **Project skill.** `skills/<name>/SKILL.md` ≤500 (waza gate): worker
   recipe — commands, gate-failing rules, owning-epics map.
3. **Waza gate.** `.waza.yaml` standard budgets; `waza check` + `waza
   tokens check` green before shipping docs/skills.
4. **Beads shape.** One objective = one epic = one owner; ≥70% → drain, not
   migrate; rivals fold with directive absorbed as DoD; gates are task-typed
   and block the closure epic; P0 = gate/incident/bottleneck only; no stale
   blocks, no inverted supersedes, no in_progress without a live worker, no
   NULL epic descriptions.
5. **Short validated slices.** One bead = one reviewable PR,
   green within a session, fast merge to the integration branch.
6. **Living docs.** Read workspace docs first; validate against
   reality; update docs in the SAME change; stale docs → bead.
7. **Validation surface.** Native gate; Python minimum: Ruff + Pyrefly +
   Pyright + Mypy + Pytest, repo-wide lint/types/tests.
8. **Lane discipline.** One bead, one branch, one worktree; never implement
   in a shared dirty checkout; merge/rollout owned by the orchestrator.
9. **Cross-repo protocol.** One beads DB per workspace owns its scope;
   cross-repo work = export/import (IDs preserved) + pointer-close + note;
   blockers across DBs are notes, never edges.
