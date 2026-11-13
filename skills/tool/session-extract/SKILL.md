---
name: session-extract
description: "session extraction, private evidence, conversation flow, rollout jsonl"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:session-extract","effective:2026-09-27","route:agent","subject:agents","supersedes:skill:claude-session-extract","supersedes:skill:poolside-session-extract","supersedes:skill:zcode-extract","usage:router"]'
---

# Session Extract

Activate only for an explicit session extraction, inspection, resumption or
reconciliation request. Resolve the configured workspace, the provider and the source
associations first, from the operator or authenticated local metadata. Do not infer the
provider from UUID shape or the workspace from conversation words, and never treat a
plan file as a transcript.

## Public pure parser

Resolve this skill's script through the authenticated governance bundle and invoke its
process CLI. No internal path import is supported. The script does no filesystem I/O and
never accepts an output-directory flag; one JSON document is emitted on stdout.

```text
extract_session.py inventory --provider <claude|poolside> --workspace <workspace>
extract_session.py extract --provider <claude|poolside> --workspace <workspace> --session-id <id>
extract_session.py extract --provider zcode --session-id <id> < authenticated-rollout.jsonl
```

### Claude and Poolside

Supply one private JSON document on stdin. The version-1 envelope has
`schema_version: 1` and a `sources` array. Each source declares `session_id`, `role`
(`metadata`, `events`, or `attachment`), an adapter-owned relative `locator`, and
`content_base64` containing the complete authenticated bytes. The existing adapter alone
discovers and reads physical files, captures metadata before selecting conversation
contents, and authenticates topology, bytes, permissions and identity through its atomic
owner.

For Claude, read top-level `cwd` metadata across all session records, including records
after queue events; assistant `message.content` blocks retain their complete original
events and `tool_use.input.file_path` becomes an unreviewed reference. For Poolside,
read `cwd` from ACP metadata records and preserve complete trajectory events, including
`tool_call.parsed`, whose `tool_call_parsed.args.path` becomes an unreviewed reference.

Inventory returns provider, schema version and matching `sessions`; a valid empty
inventory is `sessions: []`. Extraction returns private classification, selected
session, complete `events` with `event_json`, source locator and line number, unreviewed
`references`, and `attachments` pointing back into the authenticated envelope. Records
without cwd are accepted when the session has one coherent declared workspace elsewhere.
Missing or ambiguous metadata, malformed records, and unknown extraction IDs fail
nonzero without producing a result. File references are evidence, not permission to read
outside configured associations or publish their contents.

### ZCode

Inspect the configured ZCode data home. A local CLI installation may keep task metadata
in `~/.zcode/v2/tasks-index.sqlite`, model I/O in
`~/.zcode/cli/rollout/model-io-<session-id>.jsonl`, and attachments under
`~/.zcode/cli/artifacts/<session-id>/`. Confirm these paths and the task's workspace in
the live installation before reading content. Open SQLite read-only. A workspace
`.zcode/plans/plan-<session-id>.md` is a plan artifact, never conversation proof.

Feed the selected rollout JSONL on stdin and keep stdout in a private location
controlled by the caller. The result contains all distinct observed request messages
with source lines, every model response with tool calls and terminal errors, plus the
final request snapshot. Other request fields (including `body` and `headers`), response
headers, and provider metadata are omitted; these omissions do not make message contents
safe to publish. A failed model request remains failed; a missing or malformed record
or a mismatched session identity fails nonzero. Inspect referenced artifacts only
through the source adapter's authenticated association.

## Privacy and publication

Both streams are private. Never echo input or output into chat, public logs or Git. The
adapter validates the result through its typed boundary and owns all digests,
schema/driver-version cache keys, private persistence permissions and transactional
publication. There is no script snapshot or second publisher. Read the complete selected
evidence to reconstruct conversation order and the first unfinished step, and
cross-check that step against current Git, tracker, runtime and the newest operator
instruction before resuming. Summaries may aid navigation but never replace evidence.
Only explicitly classified plan artifacts pass into the documentation collector;
transcripts, credentials and raw tool-output dumps remain private; publish only bounded
findings and links to the current canonical work item.
