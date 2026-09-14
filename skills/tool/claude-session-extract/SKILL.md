---
name: claude-session-extract
description: 'claude session extraction, private evidence, conversation flow'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:claude","effective:2026-09-06","route:agent","subject:agents","usage:router"]'
---

# Claude Session Extract

Activate only for an explicit session extraction, inspection, or reconciliation
request. Resolve the configured workspace and source associations first. Do not
infer the provider from UUID shape or the workspace from conversation words.

## Public pure parser

Resolve this skill's script through the authenticated governance bundle and
invoke its process CLI. No internal path import is supported.

```text
extract_claude_session.py inventory --workspace <workspace>
extract_claude_session.py extract --workspace <workspace> --session-id <id>
```

Supply one private JSON document on stdin. The version-1 envelope has
`schema_version: 1` and a `sources` array. Each source declares `session_id`,
`role` (`metadata`, `events`, or `attachment`), an adapter-owned relative
`locator`, and `content_base64` containing the complete authenticated bytes.
The existing adapter alone discovers and reads physical files, captures metadata
before selecting conversation contents, and authenticates topology, bytes,
permissions and identity through its atomic owner. The script does no filesystem
I/O and never accepts an output-directory flag.

Read top-level `cwd` metadata across all session records, including records after queue events. Assistant `message.content` blocks retain their complete original events; `tool_use.input.file_path` becomes an unreviewed reference.

One JSON document is emitted on stdout. Inventory returns provider, schema
version and matching `sessions`; a valid empty inventory is `sessions: []`.
Extraction returns private classification, selected session, complete `events`
with `event_json`, source locator and line number, unreviewed `references`,
and `attachments` pointing back into the authenticated envelope. Records without
cwd are accepted when the session has one coherent declared workspace elsewhere.
Missing or ambiguous metadata, malformed records, and unknown extraction IDs
fail nonzero without producing a result. File references are evidence, not
permission to read outside configured associations or publish their contents.

## Privacy and publication

Both streams are private. Never echo input or output into chat, public logs or
Git. The adapter validates the result through its typed boundary and owns all
digests, schema/driver-version cache keys, private persistence permissions and
transactional publication. There is no script snapshot or second publisher.
Read the complete selected evidence to reconcile it. Summaries may aid navigation
but never replace evidence. Only explicitly classified plan artifacts pass into
the documentation collector; transcripts, credentials and raw tool-output dumps
remain private.
