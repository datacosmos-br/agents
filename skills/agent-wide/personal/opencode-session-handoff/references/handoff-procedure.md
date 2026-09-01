# OpenCode Session Handoff — Procedure

An OpenCode session record is execution evidence, not authority to repeat stale
actions.

## Preflight

1. Resolve whether the operator authorized inspection only, replan-and-pause, or
   continued execution. Session access does not imply execution permission.
2. Read the destination repository's current instructions and resolve its
   tracker, Git, projection, and runtime owners before effects.
3. Confirm the session exists. Record its id, directory, title, agent, model,
   update time, and token size.

## Export and read

Run the native export first and preserve its exit code and diagnostics:

```bash
opencode export <session-id>
```

Plugins may print warnings containing JSON before the session document. Do not
assume the first `{` begins the export, and never discard a provider or
credential error merely to make parsing succeed.

For a large session, use OpenCode's database interface read-only to recover the
cursor without loading the whole transcript:

```bash
opencode db "SELECT position, status, priority, content FROM todo WHERE session_id='<session-id>' ORDER BY position" --format json
opencode db "SELECT time_created, id, json_extract(data,'$.role') AS role, json_extract(data,'$.mode') AS mode, json_extract(data,'$.finish') AS finish FROM message WHERE session_id='<session-id>' ORDER BY time_created DESC LIMIT 50" --format json
```

Join `message` to `part` only for messages needed to recover the cursor. Inspect
text, reasoning, tool input, tool output, and tool error. Never query credential
tables or print environment secrets.

## Reconstruct and cross-check

Recover one cursor containing:

- original objective and newest operator correction;
- persisted plan and first unfinished step;
- last successful and failed commands, cwd, exit status, and decisive output;
- repositories and paths changed;
- tracker state and dependencies;
- branch, HEAD, worktree changes, and integration state;
- current runtime evidence relevant to the unfinished step;
- gates invalidated by edits, newer commits, or runtime drift.

Cross-check every continuation claim against registered state records, Git
history, measured reality, and current integrated-code intent. Correct stale
session assumptions in the proposed plan; never change reality to preserve a
stale transcript.

## Transfer to Codex

Codex owns execution after reconstruction. Do not resume OpenCode merely to
transfer ownership, copy patches out of the transcript, switch a failed model or
provider, or repeat discovery whose evidence remains current.

When approval was requested before continuation, stop after presenting what is
proven complete, what remains invalid or unfinished, owned changes already
present, the corrected ordered plan, invalidated gates, and the exact next
command. Otherwise begin only at the first unfinished step after the cross-check
passes.

## Failure and output contract

- A failed export remains failed even if database inspection succeeds; report
  both facts.
- An invalid selected credential stops that invocation without provider/model
  substitution.
- Unknown command output, exit status, dirty-file ownership, or branch owner is
  an unresolved fact to prove before mutation.
- Todos do not prove completion. Current gates, landing, runtime proof, and
  tracker closure do.

Report the session id, recovered cursor, divergences, exact evidence with cwd
and exit code, replanned steps, and status: awaiting approval, active, or
blocked.
