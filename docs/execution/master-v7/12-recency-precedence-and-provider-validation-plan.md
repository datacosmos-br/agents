# Recency precedence and provider validation plan

- **Status:** Approved and executed — etapas 1–8 merged (PRs #55, #57, #59,
  #63, #64, #65); closure of the machine-resolvable precedence gap continues
  in plan 13, which this document records but does not own
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
| 6 | Strengthen the base from findings | apply dispositions at the owners: new or reinforced rules, skills, commands, guarantee mappings, and evals, each approved as `plan-12` with its effective date; zero residue |
| 7 | Gas City agent-side cutover | semantic audit of the seven `skills/domain/gascity/gc-*` plus the two `skills/tool/gascity-*` skills against the `gc` surface (help/docs only; no orchestration executed); confirm `route:agent` and `activation:opt-in`; correct this plan's etapa-7 premise: the provider-local skill directories are owned personal projections of the canonical owner, so there is nothing to fuse or delete — deleting them would break sync convergence |
| 8 | Landing | full gate matrix green, second generation idempotent, PR merged into `dev` with every review comment resolved; stop at `dev` |

## Stop table

| Situation | Action |
|---|---|
| `effective:` source not provable | stop, list, ask the operator |
| Two owners conflict | stop, present both with numbers |
| Provider finding without a clear disposition | ask with evidence attached |
| Any red gate | fix at the owner; never route around |
| Scope expands beyond this plan | ask before continuing |

## Etapa records

### Etapa 5 — cross-provider validation (2026-08-30, read-only, bounded)

| Provider | Evidence sampled | Finding | Disposition |
|---|---|---|---|
| claude | `~/.claude/projects/-home-marlonsc-agents` (recent transcript) | governance capsule markers present — hooks inject the law | validated; no action |
| codex | 120 sessions since 2026-08-28; 100 carry `AIHUB` markers | 20 sessions lack the marker | rejected as speculative — per-session hook-install dating unavailable; re-evaluate only when reproducible |
| opencode | 10,968 sessions; most recent are `beads lote r-01..05` sweeps via beads-task-agent (2026-08-30) | tracker sweeps while Beads is formally suspended | closed as operator-authorized reconciliation (operator adjudication recorded 2026-08-30) |
| poolside | `~/.poolside/settings.local.yaml`; projection matrix | provider absent from `config/projections.json` (no hooks, no skill surface) and local allowlist contains `bash *` | accepted gap recorded (operator adjudication 2026-08-30); a poolside adapter requires separate authorization |
| omo | `~/.omo` (codegraph, lsp-daemon); process table | no live daemons at audit time | no action — living runtime registration is owned by the agents runtime, not by this plan |

### Etapa 6 — strengthening from findings (2026-08-30)

Every disposition is evidence-based; none justifies a new rule, skill, or
command today. Adding speculative governance for unproven gaps (the 20
unmarked codex sessions, a poolside adapter) would violate YAGNI and the
fail-loud contract. The rules base is validated as-is; the two operator
adjudications above are the only durable outputs, recorded here and in the
provider-evidence table.

### Etapa 7 — Gas City agent-side audit (2026-08-30)

Corrected premise with evidence: `~/.config/opencode/skills` is the opencode
personal projection destination declared in `config/projections.json`, and the
Gas City skills there carry `provenance:agents-owned` — they are owned
projections of the canonical owner, not loose copies. Nothing is fused or
deleted; deletion would break sync convergence. The nine Gas City skills
(seven `skills/domain/gascity/gc-*`, two `skills/tool/gascity-*`) remain
`route:agent`/`activation:opt-in`, verified by the catalog under `make check`.
The semantic audit against the `gc` surface is recorded in the etapa 7
commit message with the help/docs evidence.

### Etapa 4 — backfill complete (2026-08-30)

All 140 canonical artifacts (41 rules, 91 skills, 8 commands) carry exactly one
`decision:` + one `effective:` tag. Every `effective:` date is the artifact's
last Git change date; every reference resolves physically into `docs/`.
Decision mapping: `plan-00` (the master v7 authority package that approved the
current inventory) is the default; `ADR-0004` for `rules/runtime/*`,
`ADR-0005` for `governance-artifact-composition`, `plan-12` for the
precedence owner, `ADR-0007` for the bead verification law. `ADR-0007`
records the pre-existing operator approval that landed through PR #52 without
a decision document. Untagged rules received `route:both`, matching their
previous default distribution. Mandatory presence is enforced by the new
inventory-walk test in `tests/test_approvals.py`; token ceilings restored by
small prose compressions in three skills.

### Etapa 2 — precedence consolidated (2026-08-30)

`rules/coordination/operator-precedence.md` now owns the complete order and
recency mechanics: authority levels, higher `effective:` wins inside a level,
`supersedes:` resolves chains, superseded artifacts are evidence-only. The
AGENTS.md prelude keeps its one-line boot pointer; plan-scoped authority
statements (master-v7 `00-authority-and-scope.md`, session protocol, session
governance) are applications, not competing orders — verified, unchanged.

Dispositions for `docs/governance-interconnection-analysis.md` Priorities
1–10, each proved against the current inventory rather than the stale
snapshot:

| Priority | Disposition | Proof |
|---|---|---|
| 1 runtime-rule guarantees | Implemented before this plan | all 7 guarantees present in `config/governance.json` |
| 2 command guarantees | Implemented before this plan | all 7 guarantees present in `config/governance.json` |
| 3 redundant guarantees | Implemented before this plan | zero occurrences of the 5 redundant names |
| 4 four more bootstrap skills | Rejected | the active skill plans own the always-on composition; guarantees plus the router already select them on demand; the older proposal is superseded |
| 5 route tags on untagged rules | Adopted in etapa 4 | 37 of 41 rules are untagged; tags land with the mandatory approval backfill in one change |
| 6 rule cross-references | Rejected with evidence | markdown links in rules become dead links in every projection: the projection flattens `rules/runtime/fail-loud.md` into `runtime--fail-loud.md`, so `[strict-execution.md](strict-execution.md)` resolves to nothing there. `f20165a` had already reverted them for this reason; the `(rule file)` annotation is the surviving convention |
| 7 categorize the gascity rule | Implemented before this plan | `rules/gascity.md` no longer exists; owner is `rules/coordination/gascity.md` |
| 8 Gas City skills guarantee | Adopted now | `gas-city-operations` gained `skill:gascity-change-lifecycle` and `skill:gascity-workspace-lifecycle` |
| 9 orphan documents | Implemented before this plan | both guarantees present in `config/governance.json` |
| 10 guarantee coverage test | Implemented before this plan | `governance_config.py` requires exact coverage; red on the PR #52 miss proved it live |

### Etapa 8 — closure and the gap this plan did not close (2026-08-30)

Etapas 1–7 landed the approval authority, the single precedence prose owner,
the provenance in rule and command projections, and the mandatory inventory
backfill. Two conditions are recorded here rather than left implicit.

**`decision:plan-00` is umbrella scope authorization, not per-artifact
approval.** 128 of the 140 tagged artifacts carry it, pointing at
`00-authority-and-scope.md`. The backfill satisfied the format of the contract,
not its semantics. Precedence therefore must never key on `decision:`:
superseding `plan-00` would supersede 128 artifacts at once. Re-attributing
those 128 to specific decisions is deliberately out of scope — most rules do
trace to the inventory reorganization — and is recorded as an accepted
condition, never silently.

**The operator decision was not met by this plan.** "Recency-based precedence
must be machine-resolvable" required a runtime that orders artifacts. Etapas
1–4 delivered validation and rendering; nothing consumed either. The cause is
grammatical: the precedence rule says the newer artifact is "the one that
declares `supersedes:` over the older" — artifact level — while
`_SUPERSEDES_TAG` accepted only document references. Plan 13 owns the closure
and carries the evidence.

## Definition of done

1. Every active rule, skill, and command carries resolvable `decision:` +
   `effective:` into `docs/`.
2. One precedence prose owner; `grep` proves zero copies.
3. Projections regenerated; second generation identical.
4. Provider findings table complete — five providers, 100% dispositions.
5. Every Gas City skill reaches its provider destinations as an owned
   projection of the canonical owner — the etapa 7 corrected premise, not
   deletion of the provider-local directories, which would break sync
   convergence.
6. `make ci` green; PR merged into `dev`; full evidence recorded.
