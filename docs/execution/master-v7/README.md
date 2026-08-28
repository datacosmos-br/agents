# Master v7 execution package

This package is the active authority for reorganizing the existing `.agents`
inventory. It replaces master v6. Git history retains older plans; no second
active plan, compatibility copy, or manual progress ledger is permitted.

The first increment classifies and migrates only artifacts already present in
this repository. External skill or command import, ECC synchronization,
SkillShare, and FLEXT-sourced content are excluded until the current inventory
has one owner, provider projections converge, and its Waza corpus is green.
External provider specifications may be read to validate semantics and adapter
formats; reading a source does not authorize importing its artifacts.

## Fixed decisions

- Skills, commands, rules, agents, hooks, and deterministic CLI code are
  different artifact types. Provider implementation details do not collapse
  those contracts.
- Skills use distribution-first directories:
  `agent-wide`, `project-wide`, `technology`, `framework`, `tool`, and `domain`.
- Commands remain explicitly invoked commands under flat `commands/<slug>.md`.
  Their bodies may be substantially larger than skill routers and procedures.
- Paths own distribution and primary grouping. Local tags describe orthogonal
  semantics. No hand-maintained catalog may enumerate artifact identity,
  category, destination, or activation.
- Projections are independent physical copies in provider-native formats. No
  symlink, cross-repository content reference, path dependency, or fallback
  owner is allowed.
- No import starts before the existing inventory has completed the migration,
  projection, evaluation, review, and landing cycle.

## Current baseline and target

The repository snapshot inspected on 2026-08-28 is a partial, unvalidated
cutover: 76 recursively discovered skills, seven flat commands, 62 categorized
agents, 32 rules, 76 Waza skill suites, 228 skill tasks, and 133 fixtures. The
physical skill and command moves already happened, but this state is not a green
baseline: every skill description violates the active keyword-description
schema, the Waza owner still selects `gpt-5.4` instead of exact
`aihub-primary`, commands and agents lack complete semantic eval surfaces, and
rules/provider adapters are not wired through the public projection runtime.

The target is therefore not another inventory migration. It is one atomic
cutover from this partial state to strict typed owners, provider-native physical
rendering, complete offline and live gates, and integration-lane runtime proof.
Counts remain discovered consequences, never quota targets. Re-run discovery
after every owner change and fail on an unknown, duplicate, unreachable, or
unclassified artifact; never coerce one into a category to preserve a count.

## Runtime state

Beads, Dolt, and Gas City are explicitly suspended. Do not invoke, inspect,
start, migrate, select an endpoint for, or depend on those runtimes. Do not
create a substitute tracker, ledger, Markdown task list, database, workspace,
city, rig, Pack, clone, or worktree. Preserve implementation and validation
evidence only in authorized Git commits, pull requests, reviews, required
checks, and CI after Git execution is separately authorized.

While tracker closure is unavailable, a merged and post-merge-verified phase is
`LANDED_VERIFIED`, not `DONE`. The physical source move from `~/.agents` to
`~/agents`, provider-home installation, external imports, and service/timer
installation are separate increments after this repository cutover; they cannot
be smuggled into this checkout-only increment.

## Reading order

1. [Authority and scope](00-authority-and-scope.md)
2. [Artifact contracts](01-artifact-contracts.md)
3. [Skill taxonomy and migration map](02-skill-taxonomy.md)
4. [Command contract](03-command-contract.md)
5. [Agent, rule, and projection contracts](04-agent-rule-projection-contract.md)
6. [Execution phases](05-execution-phases.md)
7. [Validation and landing](06-validation-and-landing.md)
8. [Session protocol](07-session-protocol.md)
9. [Agents repository runbook](repositories/agents.md)

Architecture decisions:

- [ADR-0001: Preserve artifact-type boundaries](../../adr/ADR-0001-artifact-type-boundaries.md)
- [ADR-0002: Derive skill distribution from paths and tags](../../adr/ADR-0002-skill-distribution-paths-and-tags.md)
- [ADR-0003: Render provider-native physical projections](../../adr/ADR-0003-provider-native-physical-projections.md)

## Status vocabulary

| State | Meaning |
|---|---|
| `NOT_STARTED` | No implementation evidence exists for the phase. |
| `IN_PROGRESS` | The phase is changing its canonical owners. |
| `BLOCKED` | A required runtime, validation, review, or authority is red or unavailable. |
| `PR_OPEN` | An authorized PR targets the configured integration branch. |
| `MERGED` | The integration branch contains the approved merge commit. |
| `LANDED_VERIFIED` | Runtime and gates passed on that merge commit; tracker closure is still unavailable. |
| `DONE` | PR merged, post-merge runtime green, and canonical tracker item closed with evidence. Unreachable while the tracker is suspended. |

A local edit, test pass, commit, push, open PR, or merge without post-merge
runtime and tracker closure is never `DONE`.
