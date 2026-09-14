---
name: session-resume
description: 'session source detection, handoff cross-check, unfinished step resume'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:claude","detect:opt-in:opencode","detect:opt-in:poolside","effective:2026-09-06","route:agent","subject:agents","usage:router"]'
---

# Session Resume

Activate for an explicit request to inspect and resume a foreign session, not
ordinary continuation of the current conversation.

Resolve the selected provider and workspace from the operator's request or
configured source associations. UUID shape is not provider evidence. Missing or
ambiguous association fails closed; never probe alternate providers or guess
from conversation keywords.

Route Claude to $claude-session-extract, Poolside to
$poolside-session-extract, and OpenCode to $opencode-handoff. Read the selected
owner's complete procedure and use its current public CLI. Claude and Poolside
emit complete private structured stdout; the consumer's transaction owns
private persistence. Do not search for historical export paths or use a summary
as the only evidence.

Cross-check the full selected evidence against the current objective and newest
operator correction, plan, first unfinished step, Git state, tracker state,
last successful and failed commands, affected repositories, and integration
proof. Session history is evidence, never authority to repeat stale actions.

Continue only from the first unfinished step after the cross-check passes and
only within the operator's execution authorization. Preserve an explicit
approval pause. Missing session evidence means no execution effect; a provider
failure remains failed without substitution or reconstruction from memory.
