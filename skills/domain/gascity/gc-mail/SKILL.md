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
stored in the city's bead store. Rule `inter-session-mail` owns the obligations:
the five receipts, presence, the authority table, and the subject taxonomy. This
skill owns the commands.

## Sending

```text
xargs -0 -a body.txt gc mail send <to> -s 'Subject' -m      # Send; body from a file
xargs -0 -a body.txt gc mail reply <id> -s 'Re: topic' -m   # Reply in-thread; body from a file
```

Bodies come from a file and subjects are single-quoted (rule `bash-guard-lane-execution`).
Add `--json` to keep the returned message id: it is the "sent" receipt.

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
gc mail archive <id>                   # Close the message bead; remove from mail views
gc mail mark-read <id>                 # Mark as read without displaying
gc mail mark-unread <id>              # Mark as unread
gc mail delete <id>                    # alias for archive
gc mail check                          # Check for new mail (used in hooks)
```

`archive` and `delete` are aliases. The built-in bead-backed provider closes the
message bead instead of hard-deleting it.

- Archived messages leave mail views. Measured 2026-10-09: after an archive,
  `gc mail peek` answered `message not found`, while `bd show` still listed the
  bead as closed and `gc mail thread` no longer showed it.
- Closing does not guarantee recovery or indefinite retention.
- Require a unique message ID and authorization before either operation.
- Use `mark-read` to acknowledge without closing.
- Coordination mail is never archived while its campaign is open (rule
  `inter-session-mail`). That overrides a pack prompt's generic "read, then
  archive" advice.

## Select the city store

City mail lives in the city store. Two cases:

- Inside the city root, or inside a gc-managed session: plain `gc mail …` resolves
  the city.
- From an external session or any other checkout, use
  `direnv exec <city-root> gc --city <city-root> mail …`. Verified 2026-10-09 from
  a non-city cwd, and from inside a project environment that hid `gc` behind a mise
  error: the route resolved the host `gc` and reached the city store.

`gc` and `bd` verbs other than mail keep the owning project's home and direnv
environment (`direnv exec <project-root> …`).

A bare invocation from another directory can resolve another project's database and
fails with `PROJECT IDENTITY MISMATCH — refusing to connect` (local `metadata.json`
id ≠ database id). That is the symptom of a wrong invocation, not of the store; never
answer it with `bd init`.

## Who can be addressed (verified 2026-10-09 against `gc` 1.4.2-fc.5)

- A recipient is one of:
  - a gc session id or alias (`gc session list`, qualified as `<rig>/<agent>` or as
    an unqualified HQ alias such as `mayor`/`gastown.mayor`);
  - a configured named session;
  - `human`.
- `--from` accepts only those identities and `controller`. An external session
  (Claude Code, Codex, ZCode, Kilo) has no mailbox: `gc whoami` answers `not logged
  in`, it sends as `human`, and its identity rides in the subject
  `(<alias>@<repo>, <executor>)`.
  - Never invent an alias.
  - Never run `gc session new` to stand in for a running external executor; that
    duplicates the executor instead of registering it.
- `bd` has **no** message command (`bd message` → `unknown command`). Mail is `gc mail`
  only.

## City hall campaign (operator rule 2026-10-09)

While the city is live, city hall (the mayor, `gastown.mayor`) organizes and
coordinates external sessions through **one campaign thread**. City hall announces
that thread, and every participant reads it with `gc mail thread <thread-id>`.

`gc mail reply <id>` keeps the thread and addresses the original sender. That is how
you route inside the thread:

- **To city hall:** reply to the latest `gastown.mayor` message in the thread. The
  reply lands in the mayor's inbox and stays in the thread. Add `--notify` when city
  hall must act now.
- **To the other externals:** reply to an external's message. The reply lands in
  `human`, which every external reads.

Verified 2026-10-09: one thread listed human→human, gastown.mayor→human, and
human→gastown.mayor messages together. A fresh `send` opens a new thread; only city
hall opens one, for a new campaign.

Subjects follow rule `inter-session-mail`:
`[coord] [@<addressee>] <kind> <facts> (<alias>@<repo>, <executor>)`.

1. **Roll-call.** Reply to city hall's roll-call message with:
   - alias, executor, and repository;
   - worktree(s), branch, bead, and PR;
   - the files you hold;
   - your current state;
   - the next heavy-gate window you need;
   - your ACK of, or counter to, the protocol.
2. **Ownership before effect.** Before the first write, post the bead, the
   branch/worktree, the PR, and the exact file fence. Overlapping fences wait for city
   hall's arbitration in the thread.
3. **Gate windows.** Post `[coord] [@city-hall] gate-window START <repo> <verb>`, wait
   for city hall's ACK, run the gate, then post `END exit=<n>` with decisive output.
   One heavy gate runs per machine.
4. **Polling.** Nothing injects mail into an external session. Poll the campaign
   thread at every phase boundary and at least every 15 minutes.
5. **Receipts.** Keep the returned id. Prove readback with `gc mail peek <id>` or
   `gc mail thread`, not by filtering the unread `human` inbox. Report the sent,
   readback, ACK, accepted, and done receipts separately.
6. **Direct channels.** A provider's cross-session channel (for example
   Claude↔Claude) is only a fast path. Repeat every such message in the thread.
7. **City hall's own duties.**
   - Use `mark-read`, never archive.
   - Keep the roster and its decisions on the campaign bead.
   - Arbitrate overlaps in the thread.
   - Respect any operator scope fence on suspended rigs: no `gc sling` and no
     `gc rig resume` into them.
8. **Coordinator health.** City hall is working only if `gc session peek gastown.mayor`
   shows a model turn. If it does not, post `[coord] [@operator] blocker` to `human`
   with the peek evidence. The `coordinator-ladder` tier 2 election applies only once
   the coordinator's own runtime proves it unavailable, never on a missing reply or a
   cached status.

## Operating limits (measured)

- `gc mail send --all` reaches **only live gc sessions and excludes `human`**: for
  external sessions it reaches nobody, and with `--notify` it hangs past two minutes.
  Do not broadcast. Use `--notify` only for one named gc recipient that must act now.
- The store lock is intermittent:
  - Symptom: stderr `WARN native_store_unavailable … schema migration lock
    unavailable: timeout`, then `To diagnose: bd dolt status / Do NOT run 'bd init'`.
    The message is **not** stored.
  - That send is red. Report it with the exact stderr and diagnose with the
    read-only `bd dolt status`.
  - Do not issue it again: no retry, and no directory change to get around it. The
    store owner repairs the lock.
  - An exit code alone is not evidence: a send can look successful and store nothing.
- A listed `active` session is not a working session. From 2026-10-05 to 2026-10-09
  the city HQ stayed `active` in `gc status` and `gc session list` while every
  provider turn failed with `401 Invalid bearer token`. Only `gc session peek` showed
  it. `gc status` output is cached (`_cache_age_s`).
- Read without consuming: `gc mail peek <id>`. The operator's inbox is not yours to
  mark read. Bodies are one line; pipe them through `fold -s -w 180` to read.
