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
stored in the city's bead store. Rule `inter-session-mail` declares the obligation to
communicate only through mail. This skill owns the complete contract, because a skill
is the only governance artifact that still reaches agents beyond Claude Code.
Measured 2026-10-09: `~/.codex/skills/gc-mail` is installed, while no provider
receives the rule text.

- As an opt-in skill it reaches no project tree.
- Its delivery to each provider home is ai-hub's (rule `distribution-routing`,
  law 2).
- A session without it follows the protocol city hall posts in the campaign thread.

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
- Never archive or delete coordination mail while its campaign is open. That
  overrides a pack prompt's generic "read, then archive" advice.
- Never mark another participant's inbox read.

## Select the city store

City mail lives in the city store. Two cases:

- Inside the city root, or inside a gc-managed session: plain `gc mail …` resolves
  the city.
- From an external session or any other checkout, use
  `direnv exec <city-root> gc --city <city-root> mail …`.
  - Verified 2026-10-09 from a non-city cwd, and from inside a project environment
    that hid `gc` behind a mise error: the route resolved the host `gc` and reached
    the city store.
  - A project environment that hides `gc` is a defect of that environment's owner.
    Run mail under the city root's environment, never under another project's.

`gc` and `bd` verbs other than mail keep the owning project's home and direnv
environment (`direnv exec <project-root> …`). Rig-scoped `bd` must pass a
`bd context --json` identity check before effects.

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
- `--from` accepts only those identities and `controller`.
- Classification follows the local city registry:
  - A managed session is one gc started. `gc session list` lists it, and its
    environment carries `GC_SESSION_ID` / `GC_ALIAS`, which gc mail uses as the
    default sender.
  - An external session (Claude Code, Codex, ZCode, Kilo) has none of these, so it
    has no mailbox, sends as `human`, and carries its identity in the subject.
  - `gc whoami` reports the hosted Gas City account (`gc login`) and says nothing
    about local mail identity. Never use it for this classification.
  - Never invent an alias.
  - Never run `gc session new` to stand in for a running external executor; that
    duplicates the executor instead of registering it.
- `bd` has **no** message command (`bd message` → `unknown command`). Mail is `gc mail`
  only.

## Receipts and presence

Delivery, acknowledgement, and completion are five separate receipts; none implies
the next:

- sent: the returned message id;
- readback: `gc mail peek <id>`, or the id listed by `gc mail thread`;
- ACK: the addressee's reply in the thread;
- accepted: the owner's bead claim;
- done: command, working directory, exit code, and decisive output.

A missing reply is a missing ACK receipt and nothing more. It never proves that a
session is offline, and it never authorizes adoption, deletion, an election, or a
closure.

- The presence of an external session comes from the operator's declaration,
  confirmed by provider-native session metadata (identity, workspace, and status
  fields only; never transcripts or credentials).
- Abandonment comes only from the test in rule `bead-branch-pr-cadence` §2.

A gc-managed session is working only when `gc session peek <alias>` shows a model
turn. A status listing that reports it `active` is not proof: from 2026-10-05 to
2026-10-09 the city HQ stayed `active` in `gc status` and `gc session list` while
every provider turn failed with `401 Invalid bearer token`. `gc status` output is
cached (`_cache_age_s`).

The shared `human` inbox lists unread messages; it is not the record. An empty inbox
proves neither failed delivery nor absent progress. Prove readback from the retained
id, never by filtering the unread inbox.

## City hall campaign (operator rule 2026-10-09)

While the city is live, city hall (the mayor, `gastown.mayor`) organizes and
coordinates external sessions through **one campaign thread** (rule
`coordinator-ladder`, tier 1). City hall announces that thread, and every participant
reads it with `gc mail thread <thread-id>`.

`gc mail reply <id>` keeps the thread and addresses the original sender. That is how
you route inside the thread:

- **To city hall:** reply to the latest message whose FROM is `gastown.mayor`. That is
  the second column of `gc mail thread <thread-id>`, which lists oldest first, so the
  last match is the latest. When the thread holds no city-hall message, the guard
  exits 1 instead of printing an empty id:
  `gc mail thread <thread-id> | awk '$2=="gastown.mayor"{id=$1} END{if(id=="")exit 1; print id}'`.
  - Never reply to your own message to the mayor: a reply goes to the original
    sender, so it would land in `human` (measured 2026-10-09).
  - The reply lands in the mayor's inbox and stays in the thread. Check the
    `--json` result: its `to` must be `gastown.mayor`.
  - Add `--notify` when city hall must act now.
- **To the other externals:** reply to an external's message. The reply lands in
  `human`, which every external reads.

Verified 2026-10-09: one thread listed human→human, gastown.mayor→human, and
human→gastown.mayor messages together. A fresh `send` opens a new thread; only city
hall opens one, for a new campaign.

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
3. **Gate windows.** Post `[coord] [@city-hall] gate-window START <repo> <verb>
   <sender>` and wait for city hall's ACK. Run the gate, then post `[coord]
   [@city-hall] gate-window END <repo> <verb> exit=<n> <sender>` with decisive output.
   One heavy gate runs per machine.
4. **Polling.** Nothing injects mail into an external session. Poll the campaign
   thread at every phase boundary and at least every 15 minutes.
5. **Direct channels.** A provider's cross-session channel exists only where the
   operator authorized it: today Claude↔Claude, per tracker memory
   `operator-ruling-2026-10-09-session-channel-sendmessage`. It is a fast path:
   repeat every such message in the thread, which stays the record.
6. **City hall's own duties.**
   - Use `mark-read`, never archive.
   - Keep the roster and its decisions on the campaign bead.
   - Arbitrate overlaps in the thread.
   - Respect any operator scope fence on suspended rigs: no `gc sling` and no
     `gc rig resume` into them.
7. **Coordinator health.** If `gc session peek gastown.mayor` shows no model turn,
   post `[coord] [@operator] blocker` to `human` with the peek evidence. The
   `coordinator-ladder` tier 2 election applies only once the coordinator's own
   runtime proves it unavailable, never on a missing reply or a cached status.

## Subject taxonomy

Every coordination subject carries:
- the `[coord]` prefix;
- an optional addressee tag (`[@city-hall]`, `[@all]`, `[@operator]`,
  `[@<repo>/<executor>]`);
- a mandatory sender suffix, written `<sender>` below and meaning
  `(<alias>@<repo>, <executor>)`. External sessions all send as `human`, so the
  suffix is the only sender identity the thread carries.

A subject without the prefix is not coordination and is not read as one.

- `[coord] hello <alias> <sender>` at session start: scope, repositories, lanes,
  owning bead.
- `[coord] roll-call <sender>` collects each session's alias, scope, lanes, and file
  fence. An unanswered roll-call is a missing receipt, not an absence.
- `[coord] lane claim <canonical path> <branch> <sender>` before touching a lane.
- `[coord] lane status? <lane> <sender>` to its declared owner when the lane looks
  stalled.
- `[coord] lane changed <lane> <sha> <sender>` asking the author why. The answer is
  the attribution; it replaces the presumption of a clobber.
- `[coord] [@city-hall] gate-window START|END <repo> <verb> <sender>`, paired,
  around every heavy gate, granted by the coordinator.
- `[coord] freeze start <sender>` and `[coord] freeze end <sender>`, exact and
  paired.
- `[coord] blocker <sender>` with command, working directory, exit code, and
  decisive output.
- `[coord] landed <repo> <sha> <sender>` after every landing on an integration lane.

## Authority per question (mail is the channel, not the oracle)

| Question | Authority |
| --- | --- |
| Which managed gc actors exist | `gc agent list`, `gc session list` |
| Whether a managed session works | a model turn shown by `gc session peek <alias>` |
| Which external sessions exist | the operator's declaration, confirmed by provider-native session metadata |
| What each session is doing, its role | its roll-call reply in the campaign thread, plus the owning bead |
| Whether a lane is abandoned | the test declared in `bead-branch-pr-cadence` §2 |
| Who changed my lane, and why | the lane's log and reflog, the author's mail, the bead cited in the commit |

## Operating limits (measured)

- `gc mail send --all` reaches **only live gc sessions and excludes `human`**. For
  external sessions it reaches nobody. Every live gc session, pool agents included,
  receives a copy, which becomes an open bead assigned to that agent.
  - Measured 2026-10-09: 102 such copies kept the `bd.dog` pool draining and
    respawning (gct-lv2pe).
  - With `--notify` it hangs past two minutes.
  - Do not broadcast. Use `--notify` only for one named gc recipient that must act
    now.
- The store lock is intermittent:
  - Symptom: stderr `WARN native_store_unavailable … schema migration lock
    unavailable: timeout`, then `To diagnose: bd dolt status / Do NOT run 'bd init'`.
    The message is **not** stored.
  - That send is red. Report it with the exact stderr and diagnose with the
    read-only `bd dolt status`.
  - Do not issue it again: no retry, and no directory change to get around it. The
    store owner repairs the lock.
  - An exit code alone is not evidence: a send can look successful and store nothing.
- Read without consuming: `gc mail peek <id>`. Bodies are one line; pipe them through
  `fold -s -w 180` to read.
