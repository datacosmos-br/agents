# Runtime state ownership

The managed runtime is the systemd unit, not a process discovered by `pgrep`.
Before start/stop or an incident report, read the owner state:

- `systemctl --user is-active gascity-supervisor.service`;
- `systemctl --user status`;
- `~/.gc/supervisor.log`;
- `.gc/runtime/packs/dolt/dolt-state.json`;
- `gc order check` for overdue work.

Stop or restart only through the unit owner, never by signal to a MainPID.
Reject pgrep-only availability conclusions and synthesized success.
