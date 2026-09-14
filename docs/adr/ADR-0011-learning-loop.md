# ADR-0011: Learning loop — history to findings to governance edits

## Status

Accepted — 2026-09-05 (amended 2026-09-06: owners aligned to ADR-0008)

## Context

The operator asked for the agent-based development workflow to improve itself
from the history of every project, using this repository's documents-hub
improvement method to discover what to change in rules, skills, and commands,
with maximum automation and established external projects.

Measured on 2026-09-05 and re-measured on 2026-09-06 against `dev`:

- The improvement method exists here and is procedure-only. ADR-0006 reduces a
  historical corpus to semantic signatures routed to one owner;
  `config/governance.json` maps 74 guarantees to `rule:`, `skill:`,
  `command:`, and `document:` owners; every skill owns a waza suite with three
  roles; `make waza` verifies suites offline on every PR. The skills
  `op-learning`, `governance-audit`, and `skill-governance`
  describe the loop, and nothing triggers them mechanically.
- Since ADR-0008 this distribution has no executable: `GovernanceBundle.load()`
  is its only public surface, and AI Hub alone owns runtime effects. Model-backed
  evaluation is therefore AI Hub work; there is no `live` runner here.
- Nothing mines sessions. AI Hub declares a `continual-learning` skill that
  writes `AGENTS.md#Learned`, but the skill does not exist, its `writes` field has
  no reader, the hook payload's `transcript_path` is never read, and no
  `SessionEnd` chain is dispatched. AI Hub's `AGENTS.md` carries hand-written
  "Learned User Preferences" and "Learned Workspace Facts" sections that are a
  second owner of invariants its rules already state.
- Telemetry sinks run empty. VictoriaMetrics and VictoriaLogs are provisioned
  and receive nothing; Claude Code telemetry is disabled by host runtime
  configuration; the hook daemon logs only blocked and error outcomes.
- The corpus is large and typed: Gas City `events.jsonl` (118k events including
  968 stalled steps, 932 failed orders, 54 crashed sessions) and `usage.jsonl`;
  the OpenCode session database (10,995 sessions with cost, tokens, and diff
  size); 1,783 Claude Code transcripts; 460 Codex rollouts; 183 distilled
  operator corrections in `feedback_*.md` memories carrying their origin
  session; roughly 11,400 beads with field-change ledgers; daily provider cost
  rollups; about 5,500 agent-attributed commits.
- Ready-made projects cover parts of the problem: the native `claude plugin
  eval` harness, EvoSkill, claude-session-analyzer, coder_eval, the
  self-learning-skills promotion gate, the compound-engineering Gas City pack.

## Decision

### Owners and contract

- **agents** (this repository) owns meaning only: the guarantees and owner map
  in `config/governance.json`, the skills, rules, and commands that findings
  route to, the eval contract, and this record. It gains no executable, no
  configuration file, and no new load path; ADR-0008 stands unchanged.
- **AI Hub** owns every runtime effect of the loop: corpus paths, typed
  readers, the typed `Finding`, telemetry producers and sinks, the `SessionEnd`
  capture, routing of findings to guarantees, bead filing with ADR-0007
  evidence, and the model-backed suite runner. It exposes one verb family,
  `ai-hub learn`, whose actions are `harvest`, `route`, `snapshot`, `show`, and
  `baseline`. Routing (`signal → guarantees`) is data in AI Hub's typed
  `config/learning.yaml` and is validated at load time against the guarantee
  keys of the installed `agents-governance` bundle (`GovernanceBundle.load()`),
  which AI Hub pins as a released dependency. A signal whose guarantee does not
  exist in the bundle fails the load.
- **Gas City** owns periodicity and dispatch: formulas `learn-cycle`,
  `learn-apply`, `learn-live`, `learn-evolve`; cooldown orders at 24h, 168h,
  168h; the imported `compound-engineering` pack supplies the edit and review
  steps.

```
per session   SessionEnd/Stop -> ai-hub hook daemon -> SessionRecord + VictoriaLogs
              Claude/Codex OTEL ------------------> VictoriaMetrics/VictoriaLogs
daily         learn-cycle: ai-hub learn harvest -> ai-hub learn route -> beads (agents rig) -> gc sling learn-apply
per bead      learn-apply: edit owner artifact + waza task -> make ci (agents) -> compound-review
              -> PR --no-ff into dev -> administrative merge -> ai-hub learn baseline
weekly        learn-live: ai-hub model-backed suite run (all suites) -> results feed the next harvest
weekly        learn-evolve: EvoSkill per bad-signal skill in an isolated lane -> candidate -> learn-apply bead
```

### Findings

A finding is typed (Pydantic 2, no untyped fields) and carries: kind (operator
correction, workflow friction, behavioral quality, artifact efficacy, doc
drift), signal key, imperative `failure_pattern`, scope, evidence references
(corpus, locator, session, sequence, commit, bead, bounded excerpt, and the
read-only command that reproduces it), distinct session count, cost, first and
last seen, one to three guarantee keys, resolved owner artifacts, authority
(heuristic, operator-implicit, operator-explicit), confidence, a fingerprint
`sha256(kind|guarantee|pattern_slug|scope)`, and `not_addressed_by` naming the
owner artifact inspected and found not to cover the pattern.

Promotion to a bead requires all of: at least two sessions or one explicit
operator correction; a named imperative failure pattern; owners that resolve in
the bundle catalog; a non-empty `not_addressed_by`; and no open bead with label
`learn:<fingerprint>`. This is the self-learning-skills gate (passing check,
named failure pattern, ruled-out dead end) applied to findings.

Severity follows the governance-audit ladder: P0 for an explicit correction
recurring after its owner artifact last changed, ownerless in-flight work, or a
missing capsule in a governed checkout; P1 for friction, missed skill triggers,
cost regressions, and edits without prior read above 20%; P2 for doc drift and
remaining heuristics. Score = authority weight × log-scaled session count ×
recency decay × log-scaled cost × confidence.

Deterministic extraction covers every signal except two: clustering free-text
corrections into a pattern slug against a persisted registry, and the
"not covered" check against the owner artifact. Both use the CLIProxy alias
`aihub-primary`, log every call to a ledger, and stop the run when the safety
ceiling is hit rather than publishing a partial digest.

A weekly snapshot records every metric with the owner artifact commits it was
measured under. After an owner artifact changes, the next snapshot compares the
same metric restricted to sessions that ran under the new artifact; a worsening
above 25% files a P1 regression finding automatically.

### External projects

| Project | Decision |
|---|---|
| waza 0.38.7 | Sole eval engine. `claude plugin eval` is Claude-only and writes inside the plugin; two engines would be two writable truths. Its ablation idea is already the waza should-not-trigger role. |
| lucemia/claude-session-analyzer | Borrowed, not installed. Measured 2026-09-06: a single 1,348-line script with module-level side effects, no package, no tag, no `pyproject`, no LICENSE file (README claims MIT), and no JSON output; the PyPI name belongs to an unrelated project. Its metric definitions (read:edit ratio, edits without prior read, self-admitted errors, frustration and reasoning-loop phrase lists) are re-declared as typed fields in AI Hub. |
| sentient-agi/EvoSkill (Apache-2) | Adopted as a tool the `learn-evolve` formula runs in an isolated lane with the `script` scorer. Its skill output is a candidate; adoption goes through `learn-apply`. It never writes the canonical skill tree. |
| gascity-packs/compound-engineering | Imported into the city at the pin already used for gastown. |
| Claude Code and Codex native OpenTelemetry | Adopted, exporting only to the local Victoria sinks. |
| Kulaxyz/self-learning-skills (MIT) | Promotion gate borrowed as typed fields; not installed. |
| UiPath/coder_eval, `claude plugin eval` | Method borrowed only. |
| superpowers pack | Not imported: no consumer. |

### Residue removed in the same cutover

The hand-written Learned sections in AI Hub's `AGENTS.md` are deleted; each
bullet moves to its owner rule or to that project's docs. The
`continual-learning` declaration and the `writes` field in AI Hub's skill
schema are deleted. The two skills named `doc-drift` become one identity: the
Gas City automation is renamed `gc-doc-drift`, this repository's `doc-drift`
keeps the name. The eval fixture that named the retired CI check `Run
Evaluations` now names the real job, `Runtime-first governance validation`.

## Consequences

- Every session leaves a typed record and telemetry; every week the loop
  proposes edits with evidence, and every promoted finding is proven or
  reverted by measurement rather than opinion.
- This distribution stays read-only; AI Hub grows one verb family and all
  knobs live in its `config/learning.yaml`. The bundle's guarantee keys are
  the only coupling between the two repositories.
- Model cost is unbounded by decision; the only ceiling is the safety stop that
  fails a run loudly.
- Skills without a suite, dead references, and stale instructions become
  findings and beads instead of manual audits.

## Approval

Operator decisions, 2026-09-05: the loop runs autonomously up to an
administrative merge into `dev` — that authorization replaces only the approval
row of phase closure, every other row stays mandatory; there is no fixed model
cost ceiling; waza stays the sole eval engine; the plan's output is this record,
one umbrella epic (`gc-j0y8f`) and the rig beads (`aihub-hy4lf`, `ag-759`,
`gc-phvxb`); with the `aihub` and `agents` rigs suspended, execution is manual
in worktrees under each checkout and tracked by `bd`. Operator directive,
2026-09-06: proceed to full implementation and landing under the same
authorization.

<!-- aihub.approval: decision:ADR-0011; effective:2026-09-06 -->
