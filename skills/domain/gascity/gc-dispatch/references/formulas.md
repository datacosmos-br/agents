# Formula selection and built-ins

```
gc formula list                        # List available formulas
gc formula show <name>                 # Show formula definition
```

**Pack boundary.** Formulas come from packs; this city imports only `core`,
`bd`, and `gascity` roles (`gc import list`). Formulas outside those — the
`mol-polecat-*` family ships with the legacy polecat pack — resolve only when
that pack is imported. `gc formula show <name>` fails loud with
"not found in search paths" when it is not: treat that as a missing-import
diagnosis, never as a reason to hand-author the lifecycle.

### Choosing a work formula

Work formulas differ by **isolation** (does the agent get its own worktree and
branch?) and **handoff** (does the agent land the change itself, or hand off to
a separate merge-review step?). Reach for the lightest one that fits:

| Formula | Isolation | Lands the change | Use when |
|---------|-----------|------------------|----------|
| `mol-do-work` | none — works in the CWD | agent commits, then **closes** the bead | demos, throwaway, or a trivial single-agent fix where isolation and review are overkill |
| `mol-scoped-work` | worktree + explicit setup/teardown | agent-managed, no refinery — work modeled as a routable **step-bead DAG** | multi-step work you want decomposed into independently-routable steps under one owner, without a merge-review gate |
| `mol-polecat-work` *(legacy pack)* | worktree + feature branch | pushes the branch and **reassigns to the refinery** for merge review | production multi-agent work that must be reviewed before landing on a shared branch — requires the legacy polecat pack import; **not present in a stock city** (see pack boundary above) |

Two narrower siblings trade a stage away from `mol-polecat-work`:

- **`mol-polecat-commit`** — worktree + quality gates, but commits directly to
  the base branch (no feature branch, no refinery). For small installs where
  merge review is unnecessary.
- **`mol-polecat-report`** — no checkout; the agent investigates and writes
  findings to bead notes. For analysis/investigation beads whose output is a
  report, not a code change.

Rule of thumb: choose **`mol-scoped-work` for anything that must survive a
session recycle** — its step DAG and continuation metadata live in beads, so a
recycled agent resumes instead of stranding. Add the refinery handoff only by
importing the legacy polecat pack and using `mol-polecat-work`, which you do
only when merge review must be a distinct routed role. Drop to
**`mol-do-work`** only for the trivial single-agent case.

**When the refinery handoff doesn't apply.** `mol-polecat-work` ends by pushing a
feature branch and reassigning the bead to the refinery, which merges it into the
rig's own repo. Two kinds of work break that contract — model them as **plain
beads** with a coordinator/mayor handoff instead of attaching this formula:

- **Cross-repo / GitHub deliverables.** When the change must land in a *different*
  repo than the one the rig's refinery merges (e.g. a change to a GitHub fork PR
  rather than the rig's own repo), the refinery has nothing to merge and the
  `branch`/`target` metadata points at the wrong remote. Diverge from the formula:
  edit the fork clone, push, open the PR yourself, and hand the bead to the
  coordinator — not the refinery (gas-city precedent: gci-7ti).
- **Mayor-publish-rail beads.** When a bead is shipped-and-closed by a mayor
  publish step (not by the formula's own submit step), an attached v2 workflow
  leaves its `submit-and-exit`/`finalize` steps live and routable *after* the bead
  closes — an unrelated pool agent then claims the moot step (churn + manual
  cleanup). Until `mol-port-review` (packs#260), whose stage 3 *is* the mayor
  publish, lands, use plain beads for mayor-rail work; interim, the mayor drains
  the attached workflow at publish time.

### Built-in formulas

**mol-do-work** — Simple work lifecycle. Agent reads the bead, implements
the solution in the current working directory, and closes the bead.
No git branching, no worktree isolation, no refinery handoff. Good for
demos and simple single-agent workflows.

```
gc sling <agent> <bead-id> --on mol-do-work
```

**mol-scoped-work** — Graph-first worktree lifecycle (v2 workflow). Models the
work as an explicit DAG — a durable scope bead, explicit worktree setup and
teardown, and first-class step beads that can be routed independently, with
continuation metadata for same-session execution. The opt-in replacement for
hierarchy-first single-session formulas; agent-managed, with no refinery handoff.

```
gc sling <agent> <bead-id> --on mol-scoped-work
```

**mol-polecat-commit** — Direct-commit variant. Creates a worktree but
commits directly to base_branch with no feature branch or refinery step.
Includes preflight tests, implementation, and self-review quality gates.
For small installations where merge review is unnecessary.

```
gc sling <agent> <bead-id> --on mol-polecat-commit
```

**mol-polecat-report** — Report-only variant. No git checkout, no feature
branch, no push, no PR. The agent investigates, writes findings as bead
notes, and exits. Use for analysis or investigation tasks where the output
is a written report, not a code change.

```
gc sling <agent> <bead-id> --on mol-polecat-report
```

**mol-polecat-base** — Shared base for polecat work formulas. Defines
the common steps (load context, preflight, implement, self-review) that
variant formulas extend. Not typically used directly — use a variant
like mol-polecat-commit, mol-polecat-report, or mol-polecat-work instead.

**mol-prompt-synth** — Formula side of `gc prompt synth --writer-agent <name>`.
Reads a pre-rendered meta-prompt from disk, generates an agent prompt
template, and writes it to a destination path.

**mol-review-quorum** — Graph-first review quorum scaffold. Fans out two
read-only reviewer lanes (lane IDs, providers, models, and dispatch
targets supplied by formula variables), then routes a synthesis agent to
combine their durable structured outputs.

**mol-scoped-work** — Graph-first worktree lifecycle; the built-in v2
workflow prototype. Models work as an explicit DAG with a durable `body`
scope bead, explicit worktree setup/teardown, independently routable step
beads, and continuation metadata for same-session execution. Opt-in
replacement for hierarchy-first single-session formulas.

