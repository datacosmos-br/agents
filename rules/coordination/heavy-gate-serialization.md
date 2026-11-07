---
description: "Concurrent gates are the tools' job: agents run public make verbs at the same time in the same workspace; the owning tool (flext-infra, ai-hub) queues and coalesces identical runs and protects each file with optimistic publication. No manual gate windows, session locks or ad-hoc mutexes."
capsule_summary: |
  Operator order 2026-11-04T16:05Z supersedes ADR-0021's "one heavy gate per
  machine": manual serialization blocked every lane behind one actor and
  produced private locks, gate-window ceremonies and starvation loops. The
  integrity it protected moves into the tools that write.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-11-04","route:both"]'
---

# Concurrent gates, owned by the tools

## The rule

Any number of agents run public `make` verbs and `flext-infra` / `ai-hub`
commands concurrently in the same workspace. No session waits for a window, and
none refuses to start because another run is active.

Integrity belongs to the writing tool, never to a session protocol:

- **Optimistic publication.** A writer captures each input's state, plans, and
  publishes each file with compare-and-swap. A destination another writer
  changed first voids that write. The tool re-plans from disk, bounded by its
  configured attempts. Read-only phases (planning, scanning, gates) never hold a
  lock and never discard a whole snapshot because an unrelated file moved.
- **Queue and coalesce.** Identical requests (same verb, root and input
  fingerprint) join the running execution or reuse its recorded result.
  Different requests run in parallel. Only one atomic file effect is exclusive,
  never a whole operation.
- **One primitive.** The atomic file-change lease in flext-cli
  (`u.Cli.file_changes_lock`, behind `publish_file_changes`) is the only lock.
  It is scoped to one publication. ai-hub, generated Makefiles and services
  consume that owner. A second lock wrapper, a shell `flock`, a PID file, a
  "busy, refuse" guard or a manual `gate-window START/END` is residue to
  exterminate at its owner.

## Diagnostics discipline

- Every gate run keeps its native receipt and logs persistently. A failure
  without a captured log is re-run with capture before any code is touched.
- Slow is a signal. A step that takes multiples of its usual time is a defect
  in its owner (contention, leak, wedge, recompute), never a queue to wait out.
- A flake that only appears under concurrency is a defect in the owning tool's
  publication or isolation. Fix it there with a regression test. Never
  serialize the callers.
