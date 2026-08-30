name: gc-mail
description: 'gas city mail, inter-agent messaging, bead threads, inbox'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-mail", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check defined in
`rules/coordination/beads-verification.md` (project law): registered manual
ledgers, git history, measured reality, and the intent of the most recent
code. Declare the check and attach evidence — command, working directory,
exit code, decisive output — before closing. A bead whose premise the
current code retired is closed obsolete with evidence, never executed as
written.



# Messaging (Mail)

Mail is bead-based messaging between agents. Messages are beads with type=message, stored in the bead store.

## Sending

```
gc mail send <to> -m "message body"                    # Send a message
gc mail send <to> -s "Subject" -m "message body"       # Send with subject
gc mail reply <id> -m "reply body"                     # Reply to a message
gc mail reply <id> -s "Re: topic" -m "reply body"      # Reply with subject
```

## Reading

```
gc mail inbox                          # List unread messages
gc mail count                          # Count unread messages
gc mail peek <id>                      # Preview a message without marking read
gc mail read <id>                      # Read a message (marks as read)
gc mail thread <id>                    # Show full conversation thread
```

## Managing

```
gc mail archive <id>                   # IRRECOVERABLE: deletes the underlying bead, despite the name
gc mail mark-read <id>                 # Mark as read without displaying
gc mail mark-unread <id>              # Mark as unread
gc mail delete <id>                    # IRRECOVERABLE: alias for archive; deletes the underlying bead
gc mail check                          # Check for new mail (used in hooks)
```

`archive` and `delete` are the same operation under two names — both delete the message's underlying bead outright; neither files it away for later reading. There is no reversible "put this away" path. Prefer `mark-read` when you want a message out of the unread count without destroying it.
