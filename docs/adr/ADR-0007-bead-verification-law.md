# ADR-0007 — Bead verification law

- **Status:** Accepted
- **Date:** 2026-08-30
- **Scope:** Evidence required when a selected tracker is available

## Decision

Every bead is a hypothesis and reality is the proof. When a canonical tracker is
selected and running, creating, updating, or closing a bead requires a critical
cross-check against registered state, integration-lane Git history, measured reality,
and the most recent integrated code. Attach the command, working directory, exit code,
and decisive output. Close a premise retired by current code as obsolete with evidence;
never execute stale intent.

When the tracker runtime is explicitly suspended, create no substitute tracker or local
ledger and make no tracker-backed closure claim.
