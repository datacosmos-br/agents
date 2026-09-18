# Work Items (Beads) procedure

## Work Items (Beads)

Everything in Gas City is a bead — tasks, messages, molecules, convoys. The `gc bd` CLI
is the primary interface for bead CRUD.

### Rig-scoped beads

Each rig has its own `.beads/` database with its own ID prefix (e.g. `fe-` for frontend,
`be-` for beads). **A bead must live in the same database as the agent that will work on
it.** When you sling a bead to a rig-scoped agent, sling operates on the agent's rig
database — so the bead must already exist there. The bead ID prefix tells you which rig
it belongs to.

Use `gc rig list` to see rig names, paths, and prefixes.

### Shared execution graph

Every managed execution has one current coordination root in the city store. Search the
city store before creation. For every rig that performs a slice, create or reuse a bead
in that rig and link it with metadata `gc.shared_epic=<root>` and
`gc.shared_child=<root-child>`. The city root owns cross-rig scope, dependency order,
decisions and integration; the rig bead owns branch, exact commit, PR, gates and
repository-local next action.

At claim, every material Git or gate change, handoff and close, reread both records and
apply the four-source cross-check. Update the local evidence and the shared child's
bounded status in the same checkpoint. If either side disagrees, stop repository effects
and reconcile the canonical records. Use `gc mail` only to notify collaborators of the
bead update; never place unique status or a decision solely in mail.

When another rig produces code or generated output consumed by this slice, record its
integrated SHA as an explicit dependency transition. Adopt the producer through the
declared integration lane, revalidate the combined result, and publish consumer evidence
back to the shared graph. Do not implement a parallel owner merely because the producer
is pending.

### Creating work

**Use `--rig` to create beads in the right database.** If the work will be dispatched to
a rig-scoped agent, create the bead in that agent's rig:

```text
gc bd create "title" --rig frontend         # Create in frontend's db (fe- prefix)
gc bd create "title" --rig beads            # Create in beads db (be- prefix)
gc bd create "title"                        # Create in current directory's .beads/
gc bd create "title" -t bug                 # Create with type
gc bd create "title" --label priority=high  # Create with labels
```

### Finding work

```text
gc bd list                                # List beads in current .beads/
gc bd list --rig <rigname>                # List beads in a specific rig
gc bd ready                               # List beads available for claiming
gc bd ready --label role:worker           # Filter by label
gc bd show <id>                           # Show bead details
```

`gc ready` — the federated ready frontier across every store the city uses — landed on
`edge` **after v1.4.1**: the 1.4.1 binary rejects it as an unknown command (exit 1).
Probe with `gc ready --help` before relying on it. Its flag surface is narrower than
bd's: `--assignee`, `--unassigned`, `--metadata-field`, `--exclude-type`,
`--exclude-label`, `--sort oldest|newest`, `--limit`, `--status`, `--json` — not the
label, parent, type or priority selectors `gc bd ready` forwards. On a city that serves
a coordination class from its own `[storage]` binding, `gc bd ready` (and
`gc bd list --ready`) is refused with exit 1 and that deployment must run a build
carrying `gc ready`; on ≤1.4.1 non-split cities `gc bd ready` stays canonical.

### Claiming and updating

```text
gc bd update <id> --claim                 # Claim a bead (sets assignee + in_progress) — races in a multi-agent city; prefer `gc hook --claim` there
gc bd update <id> --status in_progress    # Update status
gc bd update <id> --add-label <key>=<value>  # Add/update labels
gc bd update <id> --append-notes "progress..."  # Append a note (does not replace existing notes)
```

### Closing work

```text
gc bd close <id>                          # Close a completed bead
gc bd close <id> --reason "done"          # Close with reason
```

### Hooks

```text
gc hook [agent]                        # Show routed work for an agent (defaults to $GC_AGENT)
gc hook --claim                        # Atomically claim one routed work item onto this agent's hook
gc hook --claim --drain-ack            # Claim; if no work, acknowledge a pending runtime drain
gc hook --claim --json                 # Emit a JSON protocol result
gc hook current                        # Print the work bead this session most recently claimed
```

### How routing reaches an agent

Routing is metadata-based, never direct dispatch. `gc sling` does not start a session —
it stamps the target and lets the reconciler decide.

- `sling_query` default: `bd update {} --set-metadata gc.routed_to=<qualified-name>`,
  where `{}` is the bead ID.
- `work_query` default resolves in three tiers:
  1. `in_progress` assigned to **this session/alias** — crash recovery;
  2. `ready` assigned to this session/alias — pre-assigned work;
  3. `ready` unassigned with `gc.routed_to=<qualified-name>` — the shared queue.

When the controller probes for demand **without session context, only tier 3 applies**.
A bead that is assigned but never routed therefore creates no pool demand.

### Claim identity — prevents duplicate work

Ownership reads and writes must use this session's own identity, not the shared template
identity:

| Line                        | Token                       |
| --------------------------- | --------------------------- |
| tier 1 crash-recovery query | `${GC_ALIAS:-$GC_TEMPLATE}` |
| claim write (`--assignee=`) | `${GC_ALIAS:-$GC_TEMPLATE}` |
| tier 2 pre-assigned query   | bare `$GC_TEMPLATE`         |
| tier 3 routed-pool query    | bare `$GC_TEMPLATE`         |

`$GC_TEMPLATE` is shared by every live session of that template; `$GC_ALIAS` is this
session's concrete identity. Using the bare template for tier 1 or the claim lets two
sessions of the same template adopt the same in-progress bead — duplicate commits, PRs,
and closes. Session and drain semantics: the gc-agents skill,
`references/lifecycle-reconciliation.md`.
