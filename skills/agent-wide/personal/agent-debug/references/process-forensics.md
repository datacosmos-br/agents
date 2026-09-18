# Process and session forensics for agent loops

## Evidence boundary

Resolve the affected user, time window, host, workspace, symptom, and permission to
inspect local process/session metadata. Preserve message bodies, prompt text, secret
values, and unrelated user activity. Record exact commands, cwd, exit, and decisive
metadata without dumping full environments.

## Attribute the producer

Build the relevant process ancestry and descendants. For each suspect record PID, parent
PID, start time, elapsed time, executable identity, argv, cwd, open target paths,
resource growth, and owning session or service when observable. Correlate that evidence
with recent agent tool invocations and filesystem timestamps inside the declared window.

Inspect persistence owners that can recreate the process: shell startup files,
environment loaders, executable shims, service or user units, timers, cron,
login/session hooks, editor/provider hooks, and declared project runtime. A deleted
executable does not prove the producer is gone if a startup owner will recreate it.

## Containment and correction

Before effects, identify exact PIDs and exact canonical source files. Do not kill all
processes sharing an interpreter name and do not recursively delete a broad binary or
configuration directory. Stop the narrow producer only when the active request
authorizes containment and its impact is known.

Correct the persistent canonical owner, not a generated loader or running symptom.
Remove only attributable generated residue through its cleanup owner. Preserve the first
failure and every unrelated process/file.

## Proof

Exercise the corrected startup or invocation path, verify the loader does not recurse or
respawn, observe the process tree for the relevant window, and prove a second invocation
is stable. Report producer, persistence owner, correction, contained PIDs/files, runtime
evidence, remaining processes, and any boundary that could not be inspected. Stable CPU
alone is not root-cause proof.
