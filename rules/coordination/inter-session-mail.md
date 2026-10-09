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
is the ledger of what was decided.

- Run every `gc` and `bd` command from the project home through its environment:
  `direnv exec <project-root> gc mail …`. `direnv exec` selects the environment;
  it does not change the process working directory. Before effects, verify that
  `bd context --json` identifies the checkout's selected project and tracker
  database. A mismatched context is not a successful preflight, even when the
  command exits zero; stop instead of initializing a store or overriding its
  endpoint to conceal the mismatch.
- Gas City's default city lookup walks the working directory. From a standalone
  project checkout, use the native `gc --city <declared-city-root> mail …`
  selector resolved by the project's configuration while retaining that project's
  working directory and environment. Do not switch project homes to make mail
  succeed; city selection and effective suspension follow `gascity` (rule file).
- A recipient is a registered session alias or `human`; `--all` reaches only live
  registered sessions and never `human`. Delivery is proven by reading the message
  back, never by the send's exit code. Retain the unique message ID and use
  `gc mail peek <id>` or `gc mail thread <id>` to inspect the available record
  without consuming the operator's inbox.
- The shared `human` inbox lists unread messages, not the complete mail record.
  Another reader can remove a message from that view by marking it read. An
  empty inbox therefore proves neither failed delivery nor absent progress;
  consult the retained IDs, thread, and owning bead instead. This is delivery
  evidence, not a promise of archived-message recovery or indefinite retention.
- Answer in-thread with `gc mail reply <id>` so the thread rebuilds the
  conversation.
- No reply means the session is not online. Act on that fact, never on a guess.

## Subject taxonomy

Subjects are filterable and recoverable; every coordination message carries one:

- `[coord] hello <alias>` at session start: scope, repositories, lanes, owning bead.
- `[coord] roll-call` for presence. Presence is answered, never inferred from a
  process, a socket, a lock, or a checkout.
- `[coord] lane claim <canonical path> <branch>` before touching a lane.
- `[coord] lane status? <lane>` to its declared owner when the lane looks stalled.
- `[coord] lane changed <lane> <sha>` asking the author why. The answer is the
  attribution; it replaces the presumption of a clobber.
- `[coord] freeze start` and `[coord] freeze end`, exact and paired.
- `[coord] blocker <alias>` with command, working directory, exit code, and
  decisive output.
- `[coord] landed <repo> <sha>` after every landing on an integration lane.

A decision, a handoff, and a blocker go to mail and to the owning rig's bead; one
without the other is not a record.

## Authority per question

Mail answers what a session says about itself. The other questions have owners:

| Question                      | Authority                                                              |
| ----------------------------- | ---------------------------------------------------------------------- |
| Which sessions exist          | `gc agent list`                                                        |
| Which are live now            | `gc status --json`, field `running`                                    |
| What each is doing, its role  | mail question and answer, plus the owning bead                         |
| Whether a lane is abandoned   | the test declared in `bead-branch-pr-cadence` §2                       |
| Who changed my lane, and why  | the lane's log and reflog, the author's mail, the bead cited in the commit |

Abandonment, adoption, and their limits are declared once, in
`bead-branch-pr-cadence` (rule file) §2. The adopter announces `[coord] lane claim`
before the first effect. Two actors on one working tree is itself a blocker:
declare it by mail before the next edit, and agree on one executor.

The `gc-mail` skill owns the procedure; this rule owns the obligation. Compose with
`fix-forward collaboration` (rule file), `multiagent edit breadcrumb` (rule file), and
`operator precedence` (rule file).
