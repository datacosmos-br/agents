---
description: "Long pre-push gates kill idle SSH connections mid-hook: persist a ServerAliveInterval keepalive in the lane's git config before the first push, and batch pushes so the gate runs once per landed stack."
capsule_summary: |
  Measured 2026-09-25/27 on gascity (pre-push matrix ≈ 15–18 min): three
  consecutive pushes failed with "Connection to github.com closed by remote
  host" because the idle SSH connection died inside the hook before the
  ref update. The fix is not a retry loop — it is a persistent keepalive in
  the worktree's git config, set once per lane.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'
---

# Pre-push keepalive and push batching

## Set the keepalive when the lane is created

```bash
git config core.sshCommand "ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=60"
```

Run it once in the lane worktree right after `worktree add`. Without it, a
pre-push hook longer than the host's idle window (gascity's `test-fast-parallel`
runs ~15–18 min) kills the connection between the hook and the ref update:
the gate is green, the push still fails, and the only way to retry is to pay
the whole matrix again.

## Batch, do not spam

Every push re-runs the full pre-push gate. Landing one commit at a time
through a heavy-hook repository pays the matrix per commit; stack the slice's
commits and push once. If a push fails on network after a green gate, fix the
transport (keepalive) — never skip the gate (`--no-verify` is a bypass).

## Gate failures need persistent shard logs

The fast-gate runner deletes its temp shard logs unless
`LOCAL_TEST_LOG_DIR` is set. Run the gate yourself with it before diagnosing:

```bash
LOCAL_TEST_LOG_DIR=$HOME/tmp/test-shards make test-fast-parallel
```

Diagnosing a push refusal without shard logs costs a full extra gate cycle.
