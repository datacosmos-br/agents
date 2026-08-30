# Recency precedence and provider validation plan

- **Status:** Approved; executing in short PR cycles, one etapa per cycle
- **Operator decision:** 2026-08-30 — recency-based precedence must be
  machine-resolvable, `docs/` owns rule approvals and dates, and recent
  executions from codex, claude, opencode, poolside, and omo validate the rules
  base before skills, rules, and commands are strengthened
- **Design authority:** `ADR-0001` (doc file), `ADR-0004` (doc file),
  `ADR-0005` (doc file), `ADR-0006` (doc file), this plan
- **Owner:** `agents` governance catalog and runtime
- **Work item:** canonical tracker suspended; no substitute tracker or ledger;
  Git, PR, review, checks, and CI are the only execution evidence

## Objective

Make the law "the newer plan imposes the stronger orientation" mechanically
resolvable: every active rule, skill, and command carries a dated, resolvable
approval reference into `docs/`; precedence prose has one owner; provider
projections carry the temporal metadata; the agent-side Gas City skills are
fused into the canonical owner; and recent provider executions validate the
rules base before and while it is strengthened.

## Decision boundary

This plan is a successor to master v7 plans 00–11 for its own scope only. It
does not distribute anything to the 52 consumer repositories; consumer
distribution remains owned by the governed project skill distribution plan
(`11-governed-project-skill-distribution-plan.md`), which stays open and
untouched. Gas City runtime is suspended: no `gc` command is invoked, no
clone, worktree, or substitute tracker is created, and evidence lives only in
Git/PR/CI. Landing stops at `dev`; promotion to `main` requires an explicit
operator request.

## Approval authority

`docs/` is the only approval authority. One reference grammar serves both
`decision:` and `supersedes:` tags:

- `ADR-<NNNN>` resolves to exactly one `docs/adr/ADR-<NNNN>-*.md`;
- `plan-<NN>` or `plan-<NN>-inc<N>` resolves to exactly one
  `docs/execution/master-v7/<NN>-*.md`; the `-inc` suffix is plan-internal.

Tag formats (all fail loud on malformed, impossible, future-dated, or
unresolvable values):

- `effective:YYYY-MM-DD` — the date the orientation became valid; never in the
  future;
- `decision:<reference>` — the dated approval this artifact operates under;
- `supersedes:<reference>` — a superseded artifact, evidence-only, never
  reactivated.

The sealed historical record under `docs/execution/` is referenced only; it is
never edited or appended to. Typed runtime
(`src/agents_governance/approvals.py`) owns formats and resolution; nothing
hand-maintained enumerates approvals.

## Interaction protocol — mandatory at every step of every etapa

1. Read the current owner; never act from memory or from a projection.
2. Use the artifact correctly in the same interaction.
3. Fix drift, ambiguity, missing tags, or duplicated prose at the owner in the
   same interaction; TODOs and deferrals are forbidden.
4. Record every semantic change with `decision:` + `effective:` at the owner.
5. Regenerate projections after any rules/skills/commands change.
6. Prove the touched scope green — zero errors and zero warnings — with
   command, working directory, exit code, and decisive output before claiming
   any state.

## Etapas

Each etapa is one objective, lands as its own short PR cycle against `dev`,
and must be green before the next begins. A red gate stops everything until
fixed at its owner.

| Etapa | Objective | Scope |
|---|---|---|
| 1 | Approval authority in `docs/` | `approvals.py` typed owner; `decision:`/`effective:`/`supersedes:` format + resolution wired into rules, skills, and commands validators; ADR README gains `Date` column; this plan doc; behavior tests. Presence is validated when the tags exist; mandatory presence for every active artifact is switched on by the same change that completes the backfill |
| 2 | Precedence consolidated | `rules/coordination/operator-precedence.md` owns the full order: authority types, then higher `effective:` wins inside a type, `supersedes:` resolves chains; the 10+ prose copies become one-line references; `config/governance.json`, evals, and skills README updated in the same change; Priorities 1–10 of `docs/governance-interconnection-analysis.md` receive explicit dispositions |
| 3 | Projection of temporal metadata | rules/commands adapters propagate approval tags into provider projections; second generation is idempotent |
| 4 | Backfill with mandatory source | every active rule, skill, and command receives `decision:` + `effective:` citing an ADR, a dated plan decision, a dated sealed-ledger entry (reference only), Git history, or a dated operator draft; underivable dates stop for the operator; the same change switches on mandatory presence |
| 5 | Cross-provider validation (read-only) | recent executions of codex, claude, opencode, poolside, and omo are audited against the rules base: claude `~/.claude/projects/` + hook logs, codex `~/.codex/sessions/` + history, opencode `opencode.db` sampled with declared date window and limits (full scans forbidden), poolside settings, omo codegraph/lsp-daemon ownership; every finding gets a dated disposition |
| 6 | Strengthen the base from findings | apply dispositions at the owners: new or reinforced rules, skills, commands, guarantee mappings, and evals, each approved as `plan-12-inc6` with its effective date; zero residue |
| 7 | Gas City agent-side cutover | semantic audit of the seven `skills/domain/gascity/gc-*` against the `gc` surface (docs/help only; no execution); fuse the Gas City skills that live outside the canonical owner in provider-local directories into `agents`; delete the local copies completely; keep `route:agent` and `activation:opt-in`; never a project projection |
| 8 | Landing | full gate matrix green, second generation idempotent, PR merged into `dev` with every review comment resolved; stop at `dev` |

## Stop table

| Situation | Action |
|---|---|
| `effective:` source not provable | stop, list, ask the operator |
| Two owners conflict | stop, present both with numbers |
| Provider finding without a clear disposition | ask with evidence attached |
| Any red gate | fix at the owner; never route around |
| Scope expands beyond this plan | ask before continuing |

## Definition of done

1. Every active rule, skill, and command carries resolvable `decision:` +
   `effective:` into `docs/`.
2. One precedence prose owner; `grep` proves zero copies.
3. Projections regenerated; second generation identical.
4. Provider findings table complete — five providers, 100% dispositions.
5. Zero Gas City skills outside the canonical owner.
6. `make ci` green; PR merged into `dev`; full evidence recorded.
