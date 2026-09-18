---
description: Exact child-process nonzero, timeout, signal, and output propagation.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:both"]'
---

# Child-process failures remain causal

Validate the executable, arguments, environment, working directory, ownership, timeout
contract, and expected publications before spawning. A child nonzero exit, timeout,
signal, spawn failure, malformed output, or incomplete publication terminates the
workflow with the native failure and captured causal evidence.

Do not use unchecked execution, shell error masking, `|| true`, exit-code remapping,
timeout-to-skip conversion, output heuristics, retries, alternate commands, or success
based on partial output. Cleanup may terminate only the process group created and owned
by this invocation; the original child failure remains the exception re-raised.

A process owned by a supervising unit is stopped through its owner, never by signal: a
`systemd --user` unit is stopped with `systemctl --user`, never `kill`, `pkill`, or
`pgrep -f ... | xargs kill`. Signaling the pid directly races the owner's own restart
policy and reports a false recovery. Triage starts with the owner before the process:
`systemctl --user list-units` for the unit's own state, then
`journalctl --user -u <unit>` for its causal history, both before any `pgrep`. Only a
process `pgrep` finds with no matching unit is orphaned and eligible for direct signal.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
