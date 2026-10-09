---
description: Every running session talks to every other session only through gc mail.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-19","route:personal"]'
---

# Inter-session communication goes through gc mail

Sessions that share a machine, a repository, or a lane talk to each other only
through `gc mail`, the city's bead-backed mail. Chat relays, notes left in a
working tree, comments in product files, and conclusions drawn from process state
are not communication. Mail is the record of what was said; the owning rig's bead
is the ledger of what was decided. A provider's direct cross-session channel is a
fast path only: every message sent through it is repeated in the gc mail thread,
which stays the record.

- City mail lives in the city store. Select it with the native
  `gc --city <declared-city-root> mail …` selector, never by moving the working
  directory. The process environment must resolve the city's pinned `gc`. When a
  project environment hides it, that is a defect of that project's environment
  owner. Until it is fixed, run the mail verb under the city root's own
  environment (`direnv exec <city-root>`), never under another project's.
- Rig-scoped `bd` keeps the project's own environment and must pass a
  `bd context --json` identity check before effects. A mismatched context stops
  the workflow; never initialize a store or override its endpoint to conceal it.
- A recipient is a gc session alias, a configured named session, or `human`.
- A session not started by gc (Claude Code, Codex, ZCode, Kilo, and the like) is an
  external session. It owns no mailbox, sends as `human`, and carries its identity
  in the subject. Never invent an alias, and never create a gc session to stand in
  for an existing external executor.
- Delivery, acknowledgement, and completion are five separate receipts, and none
  implies the next:
  - sent: the returned message id;
  - readback: `gc mail peek <id>`, or the id listed by `gc mail thread`;
  - ACK: the addressee's reply in the thread;
  - accepted: the owner's bead claim;
  - done: command, working directory, exit code, and decisive output.
- A missing reply is a missing ACK receipt and nothing more. It never proves that
  a session is offline. It never authorizes adoption, deletion, an election, or a
  closure.
  - The presence of an external session comes from the operator's declaration,
    confirmed by provider-native session metadata.
  - Abandonment comes only from the test in `bead-branch-pr-cadence` (rule file)
    §2.
- A gc-managed session is working only when it produces a model turn. A status
  listing that reports it active is not proof: such a session can fail every turn
  while it stays listed.
- The shared `human` inbox lists unread messages; it is not the record. An empty
  inbox proves neither failed delivery nor absent progress.
- Never archive or delete coordination mail while the campaign that uses it is
  open. Archiving closes the message bead and removes it from `gc mail thread`.
  Never mark another participant's inbox read.
- Answer in-thread with `gc mail reply <id>` so the thread rebuilds the
  conversation.
- While the city is live, its coordinator (city hall, `coordinator-ladder` (rule
  file) tier 1) organizes external sessions through one campaign thread. The
  `gc-mail` skill owns that procedure.

## Subject taxonomy

Subjects are filterable and recoverable; every coordination message carries the
`[coord]` prefix, an optional addressee tag (`[@city-hall]`, `[@all]`,
`[@<repo>/<executor>]`), and the sender suffix `(<alias>@<repo>, <executor>)`:

- `[coord] hello <alias>` at session start: scope, repositories, lanes, owning bead.
- `[coord] roll-call` collects each session's alias, scope, lanes, and file fence.
  An unanswered roll-call is a missing receipt, not an absence.
- `[coord] lane claim <canonical path> <branch>` before touching a lane.
- `[coord] lane status? <lane>` to its declared owner when the lane looks stalled.
- `[coord] lane changed <lane> <sha>` asking the author why. The answer is the
  attribution; it replaces the presumption of a clobber.
- `[coord] gate-window START` and `[coord] gate-window END`, paired, around every
  heavy gate, granted by the coordinator.
- `[coord] freeze start` and `[coord] freeze end`, exact and paired.
- `[coord] blocker <alias>` with command, working directory, exit code, and
  decisive output.
- `[coord] landed <repo> <sha>` after every landing on an integration lane.

A decision, a handoff, and a blocker go to mail and to the owning rig's bead; one
without the other is not a record.

## Authority per question

Mail answers what a session says about itself. The other questions have owners:

| Question | Authority |
| --- | --- |
| Which managed gc actors exist | `gc agent list`, `gc session list` |
| Whether a managed session works | a model turn shown by `gc session peek <alias>` |
| Which external sessions exist | the operator's declaration, confirmed by provider-native session metadata (identity, workspace, and status fields only; never transcripts or credentials) |
| What each session is doing, its role | its roll-call reply in the campaign thread, plus the owning bead |
| Whether a lane is abandoned | the test declared in `bead-branch-pr-cadence` §2 |
| Who changed my lane, and why | the lane's log and reflog, the author's mail, the bead cited in the commit |

Abandonment, adoption, and their limits are declared once, in
`bead-branch-pr-cadence` (rule file) §2. The adopter announces `[coord] lane claim`
before the first effect. Two actors on one working tree is itself a blocker:
declare it by mail before the next edit, and agree on one executor.

The `gc-mail` skill owns the procedure; this rule owns the obligation. Compose with
`fix-forward collaboration` (rule file), `multiagent edit breadcrumb` (rule file), and
`operator precedence` (rule file).
