# Agent Management procedure

## Agent Management

Agents are the workers in a Gas City workspace. Each runs in its own session (tmux pane,
container, etc).

### Adding agents

```text
gc agent add --name <name>             # Scaffold agents/<name>/prompt.template.md
gc agent add --name <name> --dir <rig> # Scaffold a rig-scoped agent.toml
gc agent add --name <name> --prompt-template <file>
```

### Sessions from templates

Every configured template can now spawn sessions directly.

For cities migrating off the old multi-instance model, see
`engdocs/archive/migrations/remove-agent-multi-migration.md`.

Use the session commands directly:

```text
gc session new <template>              # Create and attach to a new session
gc session new <template> --no-attach  # Create a detached background session
gc session suspend <id-or-template>    # Suspend a session
gc session close <id-or-template>      # Close a session permanently
gc session kill <name>                 # Force-kill an agent session
gc session nudge <name> <message...>   # Send text to a running agent session
gc session logs <name>                 # Show session logs for an agent
```

When multiple sessions exist for the same template, use the session ID.

### Pools

Pool capacity is agent-level configuration. `min_active_sessions` /
`max_active_sessions` are the canonical keys and **replace `pool.min` / `pool.max`**,
which survive only as legacy override fields mapped onto session scaling.
`max_active_sessions` is nil-inheriting: agent → rig → workspace → unlimited. Caps bound
controller-managed sessions; see `references/lifecycle-reconciliation.md` (skill file)
for the cap ladder, `scale_check` semantics, and routing.

### Lifecycle

```text
gc agent suspend <name>                # Suspend agent (reconciler skips it)
gc agent resume <name>                 # Resume a suspended agent
```

Effective suspension is derived from `workspace.suspended` + rig + agent, never from a
`session.suspended` event — that event type is registered but has no production emitter.

### Runtime

Process-intrinsic commands, called by agent code **from inside a session**, not by
humans. They coordinate lifecycle through session metadata.

```text
gc runtime drain <name>                # Set GC_DRAIN; ask session to wind down
gc runtime undrain <name>              # Clear GC_DRAIN and GC_DRAIN_ACK
gc runtime drain-check [name]          # Exit 0 = draining, 1 = not (for `if`)
gc runtime drain-ack [name]            # Set GC_DRAIN_ACK, then poke controller
gc runtime request-restart             # Set GC_RESTART_REQUESTED, block until killed
gc runtime heartbeat [--duration]      # Hold off idle-timeout + max-session-age
```

`drain-check` is exit-code driven — use it in a conditional, never parse stdout.
`request-restart` and `heartbeat` take the session from the current session context;
only `gc hook` resolves an agent from `$GC_AGENT` or a positional argument. Full
handshake, timeouts, and failure modes: `references/lifecycle-reconciliation.md` (skill
file).
