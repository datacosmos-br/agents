---
name: gc-mail
description: "gas city mail, inter-agent messaging, bead threads, inbox"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:gc-mail","effective:2026-11-03","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

# Messaging (Mail)

Mail is bead-backed messaging: each message is a `type=message` bead in the city store.
`rules/coordination/inter-session-mail.md` owns when actors coordinate; this skill owns
how mail is used, and `gc mail --help` owns the command grammar. A session without this
opt-in skill follows the protocol city hall posts in the campaign thread.

## Using mail

- Bodies come from a file and subjects are single-quoted
  (`xargs -0 -a body.txt gc mail send <to> -s 'Subject' -m`); `--json` keeps the
  returned message id, which is the sent evidence. `peek` reads without consuming;
  bodies are one line (`fold -s -w 180` to read).
- `archive` and its alias `delete` close the message bead, which then leaves every mail
  view with no promise of recovery; they need a unique id and authorization, and
  `mark-read` acknowledges without closing. Coordination mail is never archived while
  its campaign is open, and no one marks another participant's inbox read.
- City mail lives in the city store. Inside the city root or a gc-managed session,
  plain `gc mail` resolves it; from any other checkout use
  `direnv exec <city-root> gc --city <city-root> mail …`. A project environment that
  hides `gc` is that environment's defect.
- Other `gc` and `bd` verbs keep the owning project's environment, and rig-scoped `bd`
  passes `bd context --json` before effects. `PROJECT IDENTITY MISMATCH` means the wrong
  invocation and is never answered with `bd init`. `bd` has no message command.

## Identities

- A recipient is a gc session id or alias (`gc session list`), a configured named
  session or `human`; `--from` accepts those and `controller`. Aliases are never
  invented.
- A gc-managed session carries `GC_SESSION_ID`/`GC_ALIAS`, its default sender. A session
  gc did not start has no mailbox, sends as `human` and carries its identity in the
  subject. `gc whoami` describes the hosted account and never classifies a session;
  `gc session new` never stands in for a running external executor.

## Evidence and presence

- Sent (the returned id), readback (`gc mail peek <id>` or the id in `gc mail thread`),
  ACK (the addressee's reply in the thread), accepted (the owner's bead claim) and done
  (command, directory, exit and decisive output) are separate; none implies the next.
- A missing reply is only a missing ACK: it never proves a session offline and never
  authorizes adoption, deletion, an election or a closure. External presence comes from
  the operator's declaration, confirmed by provider-native session metadata (identity,
  workspace and status only); abandonment comes only from the inter-session rule's
  threshold.
- A gc-managed session works only when `gc session peek <alias>` shows a model turn; an
  `active` listing is not proof, and `gc status` output is cached.
- The shared `human` inbox lists unread mail. It is not the record, and an empty inbox
  proves nothing; readback is proven from the retained id.
- An exit code never proves a message was stored; readback does. A send that reports a
  store error stored nothing and is red: report its exact stderr and never resend or
  change directory to get around it.
- `gc mail send --all` reaches only live gc sessions, never `human`, and becomes an open
  bead for each of them, pool agents included; nobody broadcasts. `--notify` is only for
  one named gc recipient that must act now.

## City hall campaign

When the assignment selects a city hall campaign, city hall (the mayor session that
opens the campaign thread) coordinates external sessions through that one thread;
without a selected campaign, targeted mail is a notice and assigns nothing.
`gc mail reply <id>` stays in the thread and addresses the original sender: to reach
city hall, reply to its latest message in `gc mail thread <thread-id>` and confirm `to`
in the `--json` result; to reach the other externals, reply to an external's message,
which lands in `human`.

- **Roll-call:** each participant replies with alias, executor, repository, worktrees,
  branch, bead, PR, held files, state, next heavy-gate window and its ACK or counter.
- **Ownership before effect:** bead, branch, PR and the exact file fence are posted
  before the first write; overlapping fences wait for city hall's arbitration.
- **Gate windows:** under active city coordination, each heavy gate runs between
  `gate-window START`, after city hall's ACK, and `gate-window END … exit=<n>` with its
  decisive output. A manual execution keeps its own declared boundary and never starts
  orchestration to obtain an ACK.
- **Polling:** nothing injects mail; an external session reads the thread at every phase
  boundary and at least once per `coordination.abandonment_threshold_minutes`.
- **City hall's duties:** `mark-read`, never archive; the roster and its decisions on the
  campaign bead; overlaps arbitrated in the thread; no `gc sling` or `gc rig resume`
  into a rig the operator fenced.
- **Coordinator health:** when `gc session peek <alias>` on city hall shows no model
  turn, post `[coord] [@operator] blocker` to `human` with that evidence; the election
  in `$mayor` starts only when the coordinator's own runtime proves it unavailable.
- **Checkpoint integrator:** concurrent agents elect one checkpoint integrator on the
  campaign thread for shared records such as superproject gitlinks; the others post
  `[coord] member <repo> <sha>` per push, and an integrator silent past the abandonment
  threshold is replaced and announced.

## Shared infrastructure

A mutation of a tracker store or schema, shared daemon or port, fleet toolchain,
agent-home surface, city config or generator template is announced as
`[coord] agreement <topic>` naming every dependent it can break and an ACK deadline,
waits for ACK or an unopposed deadline, and ends with `[coord] landed <what> <version>`
naming who must upgrade.

## Subjects

Every coordination subject starts with `[coord]` and ends with the sender suffix
`(<alias>@<repo>, <executor>)`, the only sender identity an external carries; a subject
without the prefix is not coordination. Subject names follow the protocol city hall
posts in the campaign thread, and a change is attributed by its author's answer, never
by a presumed clobber.
