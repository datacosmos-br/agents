---
name: gc-mail
description: "gas city mail, inter-agent messaging, bead threads, inbox"
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gc-mail","effective:2026-08-30","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

## Verification (mandatory)

Before acting on any bead, run the four-source cross-check in
`rules/coordination/beads-verification.md` (project law) and attach the evidence it
requires.

# Messaging (Mail)

Mail is bead-based messaging between agents. Messages are beads with type=message,
stored in the bead store.

## Sending

```text
xargs -0 -a body.txt gc mail send <to> -s 'Subject' -m      # Send; body from a file
xargs -0 -a body.txt gc mail reply <id> -s 'Re: topic' -m   # Reply in-thread; body from a file
```

Bodies come from a file and subjects are single-quoted (rule `bash-guard-lane-execution`).

## Reading

```text
gc mail inbox                          # List unread messages
gc mail count                          # Count unread messages
gc mail peek <id>                      # Preview a message without marking read
gc mail read <id>                      # Read a message (marks as read)
gc mail thread <id>                    # Show full conversation thread
```

## Managing

```text
gc mail archive <id>                   # IRRECOVERABLE bead delete
gc mail mark-read <id>                 # Mark as read without displaying
gc mail mark-unread <id>              # Mark as unread
gc mail delete <id>                    # alias for archive
gc mail check                          # Check for new mail (used in hooks)
```

`archive` and `delete` are the same operation under two names — both irreversibly delete
the message's underlying bead; there is no reversible storage path. Prefer `mark-read`
to remove a message from the unread count without destroying it.

## Always from the project home, through direnv (operator rule 2026-09-19)

Every `gc` and `bd` invocation runs **from the project's own home and through its
direnv environment**: `direnv exec <project-root> gc mail …`, `direnv exec <project-root>
bd …` (or `direnv exec .` when already there). The environment selects the store and
server for that project; a bare `gc mail` from an arbitrary directory can resolve
another project's database and fails with `PROJECT IDENTITY MISMATCH — refusing to
connect` (local `metadata.json` id ≠ database id). That failure is the symptom of a
wrong invocation, not of the store, and it is never answered with `bd init`.

## Who can be addressed (verified 2026-09-19 against `gc` `edge`)

- A recipient is a **registered gc session alias** (`gc session list`, qualified as
  `<rig>/<agent>` or an unqualified HQ alias) **or `human`**. Sending to a configured
  agent that has no running session fails with `session not found`; sending to a
  suspended rig is not the problem, sending to a non-session is.
- Coding-agent sessions that were not started by `gc session new` (Claude Code, Codex,
  zcode…) are **not** gc sessions: `gc whoami` answers `not logged in`. They cannot be
  addressed by alias and they send as `human`. Until such a session is registered, the
  shared channel between all agents is the **`human` inbox**: every agent sends to
  `human` and reads `gc mail inbox human`; while the city is live, coordination also
  goes to city hall (next section).
- Put the sender alias in the subject, because every unregistered sender shows as
  `human`: `-s "[coord] hello <alias>"`, `[coord] roll-call`, `[coord] lane claim <path>
  <branch>`, `[coord] lane status? <lane>`, `[coord] lane changed <lane> <sha>`,
  `[coord] freeze start` / `[coord] freeze end`. A subject without the prefix is not
  coordination and is not read as one.
- `bd` has **no** message command (`bd message` → `unknown command`). Mail is `gc mail`
  only; it stores each message as a bead with `type=message` in the city store.

## City hall coordinates external sessions (operator rule 2026-10-09)

A session not started by `gc session new` (Claude Code, Codex, zcode, kilo) is an
**external session** of the city and its rigs. When the city is live — `gc status
--json` reports `running: true` and `suspended: false`, and `gc session list --state
active` shows the mayor — city hall (the mayor, `gastown.mayor`) is the organizer and
coordinator (rule `coordinator-ladder`, tier 1):

- Send hello, lane claims, blockers, approval requests, gate windows and landed
  receipts to the mayor by alias (`gc mail send gastown.mayor …`; `--notify` once to
  wake it) **and** mirror the same message to `human`, the bus the other external
  sessions read.
- Subjects name the executor: `[coord] <kind> <facts> (<alias>@<repo>, <executor>)`.
- Nothing injects mail into an external session: poll your threads (`gc mail thread
  <id>`) at every phase boundary and at least every 15 minutes.
- Two sessions of one executor family may also use that executor's direct channel;
  every such message is mirrored to the same gc mail thread, which stays the record.
- Heavy gates are serialized through city hall: `[coord] gate-window START <repo>
  (<alias>)` before the run and `END` after it.
- When the mayor is not active, the ladder's tier 2 applies: an election on the
  `human` thread.

## Operating limits (measured)

- `gc mail send --all` reaches **only live gc sessions and excludes `human`**: for
  coding agents it reaches nobody, and with `--notify` it hangs past two minutes. Do
  not broadcast; send to `human`. Use `--notify` only for one named registered
  recipient that must be woken.
- The store lock is intermittent even from the project home under direnv: stderr
  `WARN native_store_unavailable … schema migration lock unavailable: timeout`, then
  `To diagnose: bd dolt status / Do NOT run 'bd init'`, and the message is **not**
  stored. That send is red: report it with the exact stderr, diagnose with the read-only
  `bd dolt status`, and do not issue it again — no retry, no directory change to get
  around it; the store owner repairs the lock. **Proof of delivery is reading it
  back** — `gc mail inbox human --json`
  filtered by your subject — an exit code alone is not evidence (a send can look
  successful and store nothing).
- Answer in-thread with `gc mail reply <id>` (body from a file) so `gc mail thread <id>`
  reconstructs the conversation; a fresh `send` breaks the thread.
- `PROJECT IDENTITY MISMATCH — refusing to connect` on any mail verb means the command
  was not run through the project's direnv environment (section above); rerun it from
  the project home. Only a mismatch that survives a correct invocation is a store
  defect for the city owner.
- Read without consuming: `gc mail peek <id>`; the operator's inbox is not yours to
  mark read. Bodies are one line — pipe through `fold -s -w 180` to read them.
- No reply within a reasonable window means the session is **not online** (operator
  rule): proceed on the record you left, never on an assumed answer.

## Authority per question (mail is the channel, not the oracle)

| Question | Authority |
|---|---|
| which sessions exist | `gc agent list` |
| which are alive now | `gc status --json` → `running`, `gc session list --state active` |
| what each is doing, roles | `[coord]` mail + the owning bead |
| is a lane abandoned | the test declared in rule `bead-branch-pr-cadence` §2 |
| who touched my lane and why | lane `git log`/reflog + the author's mail + the bead cited in the commit |
