# Session recording contract

The cross-session standard for recording work so that any session — Claude,
Codex, ZCode, or a future one — can resume from the recorded surfaces instead
of rediscovering context. Authored during the 2026-09-27 governance alignment
(operator order: invest heavily in recording; the handoff is only a
reference).

## The rule

**The handoff is a reference hub, never the primary record.** Each fact lives
in exactly one canonical surface, and the handoff lists the surfaces by exact
path. Mutable references are revalidated at effect time; state is measured,
never inferred.

| Artifact kind | Canonical surface | What belongs there | What never belongs there |
| --- | --- | --- | --- |
| Command evidence | Tracker bead (note) | Command + output (or digest), pointers by path | The full narrative; status claims without output |
| Durable decision | ADR (`docs/adr/`) | Measured context, numbered decision, consequences, approval lineage | Execution status; TODOs |
| Ordered execution | Cursor plan (`.kilo/plans/<date>-<slug>/00-index.md` or `docs/plans/`) | Operator decisions in force, measured state table, ordered steps, acceptance | Decisions (link the ADR) |
| Session boundary | Handoff (`docs/handoffs/` or the lane root) | Pointers to the surfaces, owning session, "do not re-derive" list | Primary facts |
| Reusable procedure | Skill (`skills/<category>/<slug>/`) with its evals suite | Activation router + references procedure | Project-specific incident detail |
| Acting rules | Rule (`rules/<category>/<slug>.md`) | Generalized laws with approval lineage (ADR) | Per-defect catalogs |
| Critique | `Retrospectiva crítica` table inside the cursor/plan | `| Acerto ou erro | Evidência e consequência | Regra para a retomada |` | Blame without evidence |

## Startup contract

A session opens with recovery, not rediscovery: newest handoff → tracker
prime → tracker context → coordinator inbox → worktree census → environment
preflight (cgroup leaf, inherited markers, generated artifacts) → present the
cursor. Encoded as the `session-recover` command and
`rules/coordination/aihub-session-operating-rules.md` (ADR-0028).

## Coordination contract

- Multi-session work reserves shared namespaces in coordination: ADR numbers
  a rule cites must exist or be authored as coordinated authorship (marked,
  owner retains custody) — a dangling `decision:` citation breaks the whole
  bundle audit for everyone.
- Session ownership is recorded in the artifact ("the <name> session owns
  this cursor"), and lane claims are reported to the coordinator at claim and
  at landing, delivery proven.
- Critique of another session carries evidence and proposes the rule that
  prevents the repeat; it never renames or deletes the other session's
  in-flight work.

## Completion test

A recording is complete when a newcomer can (a) know the measured state
without asking, (b) execute the next step without re-deriving, and (c) not
repeat the recorded mistakes. All three, or the recording is not done.
