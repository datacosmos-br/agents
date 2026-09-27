---
description: Acting rules for agent sessions working the mcb project.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'
---

# mcb session operating rules

Acting rules for any agent session working `marlonsc/mcb` (distilled from
operator directives 2026-09-24..27; each rule earned the hard way — the full
context lives in the beads and ADRs referenced at the end).

## Integration law

- Work outside an integrated PR is lost work. Land in small cycles: lane →
  gates → PR → no-ff merge to `develop` → close the bead with evidence →
  retire the lane. Target minutes, not hours, between green gates and merge.
- Every lane is a dedicated `git worktree` with a **physical** `.venv`
  (`make setup`) and `direnv allow`. Never a symlinked venv, never the primary
  checkout, never `/tmp`.
- Before assuming any bead, search for pre-existing work: open PRs, remote
  branches, and upstream WIP. Adopting someone's abandoned work is right;
  redoing or duplicating active work is a firing offense.
- Never touch a lane/branch that another agent is actively driving (proven
  recent commits). Coordinate instead.

## Beads law

- A bead untouched for more than 1 hour is abandoned — claimed, deferred, and
  blocked included. Assumed beads get a lane note comment at claim time.
- Housekeeping duty: dedupe, close superseded, realign epics, fix titles.
  `--force` is pre-authorized to unlock beads; record why in the bead.
- Closing requires evidence: merge commit, captured gate rc, or structural
  proof written into the bead. "Done" without a command output is a lie.

## Coordination law

- Report bead/branch/PR to the coordinator (`gc mail send human`) when
  starting work and when landing it.
- Critique other sessions' violations with evidence, never blame without it.

## Verification law

- An exit code is not evidence: read the log (`test result:`, the assertion)
  before declaring RED or GREEN. Compile failures are not test failures.
- Local make gates are the only CI (GitHub CI is off): `make gen check`,
  `CI=Y make check`, `CI=N make check`, `make test`,
  `make rust WHAT=test` — each isolated, rc captured, zero-execution results
  are RED, never "passed".
- Root cause only: no bypass, no shim, no retry, no catch-normalization, no
  silent filtering. A warning beats silence; a fix beats both.

## mcb-specific quirks (breaking these wastes hours)

- `make test WHAT=rust` is a retired selector that silently collects 0 tests;
  the rust gate is `make rust WHAT=test` with `ORT_DYLIB_PATH` and
  `CARGO_HOME` exported (see the mcb.lane-ops skill and bead mcb-hsro).
- mise lock/install only with the aube-capable receipt mise
  (`~/.local/share/mise/bootstrap/mise-2026.9.15`); the host mise corrupts npm
  tool installs.
- Mimosa hook: write source via Write/Edit tools, never Bash heredocs; clippy
  denies `expect_used` in tests and `-D unused-variables` everywhere.
- Mimosa sealed scans recur on disposed anchors: dispositions live in beads
  and in `docs/adr/059-mimosa-advisory-triage-policy.md` (rules D1–D5). A
  re-reported anchor with a bead disposition closes by reference.

## Stop-and-ask triggers

Contract conflicts, authority boundaries (operator-only mutations), and any
case where two rules collide: present both rules with references and ask.
