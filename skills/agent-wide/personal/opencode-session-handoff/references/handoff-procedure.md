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

Write the native output and diagnostics to private files below OpenCode's
reported data directory, validate the complete document, and retain an invalid
or truncated result with an explicit `.invalid` name. A transport or tool-output
capture limit does not prove that the native exporter truncated its file; always
validate the file written directly by the command. Never publish these files
or place them in a source checkout.

After recording the native result, use the skill's snapshot script to produce a
separate allowlisted database snapshot and sanitised handoff:

```bash
python scripts/export_session_snapshot.py <session-id>
```

The script resolves the data directory from `opencode debug paths`, opens its
reported SQLite database with `mode=ro` and `query_only`, validates a strict
table/column allowlist, and queries only session, todo, message cursor metadata,
and part cursor metadata. It incorporates a validated native export when present, writes
atomically with directory mode `0700` and file mode `0600`, and redacts secret
keys and credential-shaped text from the Markdown handoff. The private JSON may
contain raw tool output and remains sensitive. It is evidence recovery, never a
fallback that changes the status of the native export.

For a large session, use the generated private snapshot to recover the cursor
without loading the whole transcript through a bounded command-output channel.
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
