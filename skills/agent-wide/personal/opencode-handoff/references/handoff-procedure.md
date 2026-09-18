# OpenCode Session Handoff — Procedure

An OpenCode session record is execution evidence, not authority to repeat stale actions.

## Preflight

1. Resolve whether the operator authorized inspection only, replan-and-pause, or
   continued execution. Session access does not imply execution permission.
2. Read the destination repository's current instructions and resolve its tracker, Git,
   projection, and runtime owners before effects.
3. Confirm the session exists. Record its id, directory, title, agent, model, update
   time, and token size.

## Export and read

Run the skill's deterministic exporter. It invokes the native export first and preserves
its exit code and diagnostics before reading the database:

```bash
python scripts/export_session_snapshot.py <session-id>
```

Plugins may print warnings containing JSON before the session document. Do not assume
the first `{` begins the export, and never discard a provider or credential error merely
to make parsing succeed.

The script resolves OpenCode's data owner with `opencode debug paths`, writes native
stdout and stderr directly to private files, validates the complete native document, and
retains an invalid result with an explicit `.invalid` name. It opens the reported
`opencode.db` through SQLite URI `mode=ro`, enables `query_only`, validates a strict
table/column allowlist, and exports the exact session's complete message and part JSON,
including text, reasoning, tool input, tool output, and tool error. The directory is
published atomically below the OpenCode data owner's `exports/<session-id>/` path with
mode `0700`; every file has mode `0600` and every source has a SHA-256 digest in
`manifest.json`.

The database snapshot and native logs are private and may contain raw tool output. Only
`handoff.sanitised.md` redacts secret keys and credential-shaped text for operator
review. A failed or invalid native export makes the command nonzero after the evidence
directory is published; database success never changes that native status.

For a large session, read only the generated sanitised handoff and query the private
snapshot locally for additional exact message ids. Never print the raw snapshot, query
credential tables, or expose environment secrets.

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

Cross-check every continuation claim against registered state records, Git history,
measured reality, and current integrated-code intent. Correct stale session assumptions
in the proposed plan; never change reality to preserve a stale transcript.

## Transfer to Codex

Codex owns execution after reconstruction. Do not resume OpenCode merely to transfer
ownership, copy patches out of the transcript, switch a failed model or provider, or
repeat discovery whose evidence remains current.

When approval was requested before continuation, stop after presenting what is proven
complete, what remains invalid or unfinished, owned changes already present, the
corrected ordered plan, invalidated gates, and the exact next command. Otherwise begin
only at the first unfinished step after the cross-check passes.

## Failure and output contract

- A failed export remains failed even if database inspection succeeds; report both
  facts.
- An invalid selected credential stops that invocation without provider/model
  substitution.
- Unknown command output, exit status, dirty-file ownership, or branch owner is an
  unresolved fact to prove before mutation.
- Todos do not prove completion. Current gates, landing, runtime proof, and tracker
  closure do.

Report the session id, recovered cursor, divergences, exact evidence with cwd and exit
code, replanned steps, and status: awaiting approval, active, or blocked.
