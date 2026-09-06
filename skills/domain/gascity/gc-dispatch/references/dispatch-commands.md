# Dispatching Work — Commands

`gc sling` routes work to session configs. **Multi-session configs are valid
targets** — sling to the config and any eligible session can claim the work.
You do NOT need to find or create an individual session first.

## Quick reference

```
gc sling <bead-id>                     # Auto-target via rig's default_sling_target
gc sling <session-config> <bead-id>     # Route to a specific session config
gc sling <session-config> -f <formula>  # Instantiate formula, route its root (v2 → workflow)
gc sling <session-config> <bead-id> --on <formula>  # Attach formula to existing bead (v2 → workflow)
```

## Targeting

The `<session-config>` is a qualified config name from `gc session list`:
- **Single-session config:** `mayor`, `hello-world/refinery`
- **Multi-session config:** `hello-world/polecat` — routes to the config's shared work queue

**1-arg shorthand:** When target is omitted, sling derives it from the
bead's rig prefix. The rig's `default_sling_target` in city.toml determines
where work goes. Example: bead `hw-42` → rig `hello-world` → target
`hello-world/polecat`.

**Rig-scoped beads:** `gc sling` automatically resolves the rig directory
for rig-scoped bead IDs (e.g. `hw-abc`) and runs `gc bd update` from there,
so the rig's `.beads` database is found without manual intervention.

**Beads must be in the agent's rig database.** Sling operates on the
target agent's rig database — formula cooking, labeling, and convoy
creation all happen there. Create the bead in a specific rig's database
with `gc bd create --rig <rig>`, which resolves the rig from city config
and uses its database and prefix:

```
gc bd create "fix the bug" --rig frontend   # Creates fe-xxx in frontend's db
gc sling frontend/polecat fe-xxx            # Works — bead is in the right db
```

If the bead is in the wrong database (e.g. `gc-xxx` in HQ but targeting
a frontend agent), sling's cross-rig guard will block the route.

## Direct dispatch (bead to session config)

```
gc sling <session-config> <bead-id>    # Route a bead to a session config
gc sling <bead-id>                     # Use rig's default_sling_target
```

The agent receives the bead on its hook and runs it per GUPP.

## Formula dispatch (`-f`, formula creates its own root bead)

```
gc sling <agent> -f <formula>          # Instantiate a formula, route its root bead
```

Instantiates the formula and routes its **root bead** to the target. What the
instantiation produces depends on the formula's compiler contract: a **v2**
formula (one declaring `[requires] formula_compiler = ">=2.0.0"`) starts a
**workflow**; a **v1** formula instantiates a **wisp** (an ephemeral molecule).
Use `-f` when the formula defines the work itself — when you already have a work
bead, use `--on` (below). A formula that references `{{convoy_id}}` or contains
a drain step cannot be launched bare with `-f`; route it onto a bead with `--on`
so a target convoy is created.

**Formula-on-bead dispatch (`--on`, formula runs against an existing bead)**

Flags that matter on every sling (verify with `gc sling --help`):

| Flag | Effect |
|------|--------|
| `-n, --dry-run` | show what would be routed without executing — preflight a dispatch |
| `--force` | suppress warnings, allow cross-rig routing and v2 workflow replacement |
| `--merge direct\|mr\|local` | merge strategy stamped on the auto-convoy |
| `--var key=value` | formula variable substitution (repeatable) |
| `--no-convoy` | suppress the ordinary routing auto-convoy (not the v2 input convoy) |
| `--owned` | mark the auto-convoy as owned (manual lifecycle, closed by `gc convoy land`) |
| `--no-formula` | route the raw bead even when a default formula applies |
| `--reassign` | clear any human assignee before routing (human→pool handoff) |
| `--title`, `--stdin` | wisp root title / read bead text from stdin |
| `--scope-kind/--scope-ref` | logical workflow scope for v2 launches |

## Who advances a v2 workflow

A v2 workflow is **orchestrator-driven, not agent-driven**. The control
dispatcher (the `core.control-dispatcher` session) executes every **control
bead** — check, retry, fan-out, tally, drain, scope-check, workflow-finalize:
it evaluates budgets, expands fan-outs, scatters drains, and finalizes the
workflow. **Agents execute only plain step beads** — independently routable
work claimed through the hook. If workflow steps sit open, check the
dispatcher session before nudging workers; if it is stopped, nothing advances
the graph no matter how many agents are alive. (`docs/reference/specs/
formula-spec-v2.md` sec 0.2.)

```
gc sling <agent> <bead-id> --on <formula>  # Attach a formula to an existing bead
```

`--on` attaches a formula to a bead that **already exists** — the bead is the
work; the formula supplies the method. What gets created depends on the
formula's compiler contract:

- **v2 formula** (`[requires] formula_compiler = ">=2.0.0"`) — starts a
  **workflow**. The sling creates a workflow-root bead **and** an auto-convoy,
  with your bead tracked as the work member (root + convoy + work bead). The
  step DAG and handoff metadata (`branch`, `target`, …) are persisted as beads,
  so they survive a session recycle — a recycled agent resumes the same branch
  instead of stranding it.
- **v1 formula** — instantiates a **wisp** (an ephemeral molecule) in place on
  the bead.

**Convoy-referencing formulas require a target convoy.** A v2 formula that
references `{{convoy_id}}` or contains a drain step must launch onto a convoy —
routing with `--on` satisfies that, because the sling normalizes the target into
an **input convoy**, creating a one-item convoy that tracks your bead when the
target is not already a convoy. That input convoy is not optional: `--no-convoy`
suppresses only the ordinary routing auto-convoy, not the v2 input convoy. To run
the workflow against a convoy you already have, pass that convoy as the target
(`gc formula cook <formula> --attach <convoy-id>`). Launching such a formula bare
with `-f` is rejected.

