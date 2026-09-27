---
name: zcode-session-extract
description: "zcode session extraction, rollout jsonl, private conversation evidence"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:zcode","effective:2026-09-27","route:agent","subject:agents","usage:router"]'
---

# ZCode Session Extract

Activate for an explicit request to inspect or resume a ZCode session. Resolve the
workspace and session identity from the operator or authenticated local task metadata.
Do not infer the provider from the UUID or treat a plan file as a transcript.

## Locate the evidence

Inspect the configured ZCode data home. A local CLI installation may keep task metadata
in `~/.zcode/v2/tasks-index.sqlite`, model I/O in
`~/.zcode/cli/rollout/model-io-<session-id>.jsonl`, and attachments under
`~/.zcode/cli/artifacts/<session-id>/`. Confirm these paths and the task's workspace in
the live installation before reading content. Open SQLite read-only. A workspace
`.zcode/plans/plan-<session-id>.md` is a plan artifact, never conversation proof.

## Extract privately

Resolve this bundle's `scripts/extract_zcode_session.py` through the authenticated
governance bundle. Feed the selected rollout JSONL on stdin; keep stdout in a private
location controlled by the caller. The script performs no filesystem I/O and accepts
one explicit session ID:

```text
python extract_zcode_session.py extract --session-id <id> < authenticated-rollout.jsonl > private-result.json
```

The result contains all distinct observed request messages with source lines, every
model response with tool calls and terminal errors, plus the final request snapshot.
The request headers, request body, response headers, and provider metadata are omitted.
These omissions do not make message contents safe to publish. Read the complete private
result to reconstruct conversation order and the first unfinished step. A failed model
request remains failed; a missing or malformed record fails nonzero. Inspect referenced
artifacts only through the source adapter's authenticated association.

Cross-check the recovered step against current Git, tracker, runtime, and the newest
operator instruction before resuming. Keep session evidence private; publish only
bounded findings and links to the current canonical work item.
