# ADR-0007 — Bead verification law

- **Status:** Accepted
- **Date:** 2026-08-30
- **Scope:** Mandatory four-source cross-check for every bead at creation, update, and close
- **Relates to:** Plan 12 (`12-recency-precedence-and-provider-validation-plan.md`), `rules/coordination/beads-verification.md`, Gas City surface law
- **Records:** The operator-authored bead verification law landed through the merge of PR #52 (commit `2c792da`, 2026-08-30) without a decision record. This ADR documents that existing approval; it introduces no new decision.

## Decision

Every bead is the hypothesis; reality is the proof. Closing a bead requires a
critical cross-check against four independent sources — registered state
records, git history, measured reality, and the intent of the most recent
integrated code — with command, working directory, exit code, and decisive
output attached. A bead whose premise the current code retired is closed
obsolete with evidence, never executed as written.
