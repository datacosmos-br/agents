---
name: gc-city
description: "gas city lifecycle, city init, start stop, supervisor status"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:gc-city","effective:2026-11-03","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

# City lifecycle

A city is a directory with `city.toml` and `.gc/` runtime state; `gc --help` owns the
command grammar (`init`, `start [--dry-run]`, `stop`, `restart`, `status`, `suspend`,
`resume`, `config show|explain`, `doctor`, `events`, `pack list|fetch`).

- Orchestration is selected only by the current operator request and the repository's
  association with a city, never by an installed binary, a directory or a running
  process. The selected city's pinned release owns its roles, topology and runtime
  state, which change only through its native commands in an authorized cutover; its
  materialized provider files are runtime state, never source; and suspension grants
  no session, dispatch, topology change or resume.
- Whether a mayor or supervisor coordinator is active is read from `gc status` at every
  phase boundary and recorded on the active bead, never inferred from a binary, a
  process or an earlier session.
- The managed runtime is its systemd unit, never a process found by `pgrep`. Before a
  start, a stop or an incident report, read the unit
  (`systemctl --user status gascity-supervisor.service`), the supervisor log
  (`~/.gc/supervisor.log`) and `gc order check`; stop or restart only through the unit
  owner, never by signal, and never report success the unit does not show.
- `gc init` and `gc start` register the city and reconcile at once. One supervisor
  (`gc supervisor run`) hosts one lock-enforced reconciliation runtime per city; tick
  timing and `[daemon]` keys are in `references/reconciliation-timing.md`.
- Interactive sessions start with `gc session new <template>`; the dashboard is the
  gc-dashboard skill, and packs add `gc <pack> <command>` subcommands and doctor checks.
