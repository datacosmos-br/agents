# Runtime-heal procedure

Ordered checklist for recovering a failed runtime service (ai-hub fleet
shapes; generalize the owners, keep the discipline). Every step ends in a
captured command. Sources of truth: the service's own journal, the decision
records the project declares, and the live endpoints — never a remembered
state.

## 0. Preflight (environment truth)

1. `systemctl --user list-units '<prefix>-*' --all` — which services are
   failed/inactive/active; record the invocation.
2. Environment truth per ADR-0028: read the process's own cgroup
   (`cat /proc/self/cgroup`, rightmost `.service`/`.scope` segment decides).
   Inherited `INVOCATION_ID`/`SYSTEMD_EXEC_PID`/`GC_SUPERVISOR_*` are not
   evidence of unit membership.
3. If a credential-projection guard refuses an operator-session action, the
   guard is the defect when the cgroup leaf is a `.scope`; cure the guard at
   its owner. `env -u <MARKER> <command>` is a forbidden bypass.
4. Fresh worktree: run the repository's generator verb (e.g. `make gen`)
   before any battery — generated artifacts (receipts, locks) are part of an
   honest run.

## 1. Diagnose at the failing layer

1. Read the failing unit's journal (`journalctl --user -u <unit> -n 200`) to
   the raw traceback; the first exception is the layer.
2. Name the owner the traceback names: a validator → the model contract; a
   resolver → the graph/index owner; a transport → the client owner. Cure at
   the owner, never around it.
3. Check whether the installed runtime contains the cure
   (`<runtime>/releases/<id>` provenance, `direct_url.json` commit versus the
   lock). A ghost release replays old bugs after correct source fixes.

## 2. Publication contracts (model-pipeline shape)

1. The snapshot validator refuses any active, selectable inventory model
   without a resolved catalog model under its exact identity — resolution, not
   exclusion, is the only survivable outcome for a selectable model.
2. Channel-identity models (provider = runtime channel) normalize to their
   unique canonical catalog entry; the published identity stays the served
   identity; route facts fall back to the canonical entry's own provider
   (ai-hub ADR-0031). A normalization without an audit log is a defect.
3. Publication is compare-and-swap: build snapshot gen N+1, PUT with expected
   gen N, verify the receipt digest against the snapshot's own digest. A
   mismatch is fail-loud, never retried silently.
4. The active-state mirror is written only through its declared owner API
   (atomic write + read-back); hand-writing state files is corruption.

## 3. Activation contracts

1. `install` is the development contract (a release built from one identified
   local worktree); `deploy` is the production contract (the attested
   published release). Never fall back between them.
2. Run `install` from the checkout that holds the cure, twice; the second run
   must produce zero diff (idempotency proof).
3. Dependent services restart through the install flow, not hand restarts;
   prove sockets and units after, not during.

## 4. Readiness evidence (activation ≠ readiness)

1. Daemon reaches its ready/healthy state with a published generation the
   remote accepted (journal lines + endpoint response captured).
2. End-to-end probes through public surfaces only (`status`, health-check,
   doctor verbs); no private method or source-text assertions.
3. Record the evidence on the tracking bead: installed release id, generation
   number, receipt digest, unit states. Then close.

## Traps (each earned in the 2026-09 campaigns)

- A test battery red under an agent shell is often the environment (inherited
  unit markers, missing generated artifacts, worktree-path substring
  collisions) — attribute before curing code.
- Exit code zero with empty output is RED.
- The dashboard port may serve HTML where the API lives elsewhere; resolve the
  management route from configuration before probing.
- Coordination surfaces (tracker store, coordinator inbox) are resolved
  through their declared owners (`direnv`, city routes), never assumed ports.
