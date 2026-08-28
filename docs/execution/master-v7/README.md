# Master v7 execution package

This package is the active authority for reorganizing the existing `.agents`
inventory. It replaces master v6. Git history retains older plans; no second
active plan, tracker, ledger, or compatibility copy is permitted. While
canonical tracking is suspended, create no substitute state owner and preserve
evidence only in separately authorized Git/PR/CI surfaces.

The first increment classifies and migrates only artifacts already present in
this repository. External skill or command import, ECC synchronization,
SkillShare, and FLEXT-sourced content are excluded until the current inventory
has one owner, provider projections converge, and its Waza corpus is green.
External provider specifications may be read to validate semantics and adapter
formats; reading a source does not authorize importing its artifacts.

## Fixed decisions

- Skills, commands, rules, agents, and deterministic CLI code are
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
- Agent runtime has one public facade: the optionless `agentsctl` verbs `help`,
  `doctor`, `check`, `sync`, `evaluate`, `secure`, `clean`, and `live`. Make is
  development support and gate composition, never a second runtime API.
  Repository hooks are not an alternate execution surface and do not exist.
- All workflows use strict fail-loud execution. The first exception and causal
  chain escape unchanged; complete preflight precedes effects; validators stop
  at the first defect; keyring, retries, fallbacks, undeclared, competing, or
  error-triggered defaults, compatibility, partial execution, and error
  normalization are prohibited. Canonical calculated defaults remain at one
  typed owner and are omitted from consumers.
- No import starts before the existing inventory has completed the migration,
  projection, evaluation, review, and landing cycle.

## Current baseline and target

The repository snapshot inspected on 2026-08-28 is an open cutover with
recursively discovered skills and Waza suites, flat commands, categorized
agents, and typed rules. Skill descriptions now satisfy the strict
keyword/nominal-phrase schema, the command surface owns seven independent eval
suites, and the Waza configuration selects exact `aihub-primary`. These are
work-lane facts, not phase completion: deterministic command/agent/rule native
rendering evals and the projection v5 implementation exist, while complete
runtime evidence, full provider evidence, offline/live Waza results, integrated
gates, review, merge, and post-merge validation remain open.

The target is therefore not another inventory migration. It is one complete
cutover from the current work-lane state to strict typed owners, provider-native
physical rendering, complete offline gates, applicable external-token gates,
and integration-lane runtime proof.
Counts remain discovered consequences, never quota targets. Re-run discovery
after every owner change and fail on an unknown, duplicate, unreachable, or
unclassified artifact; never coerce one into a category to preserve a count.

## Runtime state

Beads, Dolt, Gas Town, and Gas City are explicitly suspended. Do not invoke,
inspect, start, migrate, select an endpoint for, or depend on those runtimes.
Create no alternate database, tracker, ledger, workspace, city, rig, Pack,
clone, or worktree. Preserve validation evidence in authorized Git
commits, pull requests, reviews, required checks, and CI after Git execution is
separately authorized.

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
9. [Plan 1: skills strict execution](08-skills-strict-execution-plan.md)
10. [Plan 2: runtime extermination](09-runtime-extermination-plan.md)
11. [Additive capability composition](10-additive-capability-composition-plan.md)
12. [Agents repository runbook](repositories/agents.md)

Approved successor increment, gated on this package being integrated and
revalidated on `main`:

13. [Governed project skill distribution](11-governed-project-skill-distribution-plan.md)

Architecture decisions:

- [ADR-0001: Preserve artifact-type boundaries](../../adr/ADR-0001-artifact-type-boundaries.md)
- [ADR-0002: Derive skill distribution from paths and tags](../../adr/ADR-0002-skill-distribution-paths-and-tags.md)
- [ADR-0003: Render provider-native physical projections](../../adr/ADR-0003-provider-native-physical-projections.md)
- [ADR-0004: Enforce one optionless fail-loud runtime CLI](../../adr/ADR-0004-optionless-fail-loud-cli.md)
- [ADR-0005: Compose governance and native lifecycle delivery](../../adr/ADR-0005-composed-governance-delivery.md)
- [ADR-0006: Synthesize historical governance by behavior](../../adr/ADR-0006-semantic-governance-synthesis.md)

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

`BLOCKED` is an active phase state, not abandonment. Red checks and review
findings require owner correction and fresh publication; pending independent
approval requires solicitation or operator help after the technical surface is
green. No state in this table authorizes switching work without an explicit
operator pause, reorder, or replacement.
