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
gc mail send <to> -m "message body"                    # Send a message
gc mail send <to> -s "Subject" -m "message body"       # Send with subject
gc mail reply <id> -m "reply body"                     # Reply to a message
gc mail reply <id> -s "Re: topic" -m "reply body"      # Reply with subject
```

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
  `human` and reads `gc mail inbox human`.
- Put the sender alias in the subject, because every unregistered sender shows as
  `human`: `-s "[coord] hello <alias>"`, `[coord] roll-call`, `[coord] lane claim <path>
  <branch>`, `[coord] lane status? <lane>`, `[coord] lane changed <lane> <sha>`,
  `[coord] freeze start` / `[coord] freeze end`. A subject without the prefix is not
  coordination and is not read as one.
- `bd` has **no** message command (`bd message` → `unknown command`). Mail is `gc mail`
  only; it stores each message as a bead with `type=message` in the city store.

## Operating limits (measured)

- `gc mail send --all --notify` hangs and is killed by a timeout; broadcast **without**
  `--notify`, and use `--notify` only for one named recipient that must be woken.
- The store lock is intermittent (`schema migration lock unavailable: timeout`): a send
  that times out may still have created the bead — check `gc mail count` before
  resending, and prefer one longer timeout over repeated short ones.
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
| is a lane abandoned | unanswered `[coord] lane status?` + registration proof + publication proof + fresh backup |
| who touched my lane and why | lane `git log`/reflog + the author's mail + the bead cited in the commit |
