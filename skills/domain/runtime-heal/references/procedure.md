# Runtime-heal procedure

Ordered checklist for recovering a failed declared runtime service.
Every step ends in a
captured command. Sources of truth: the service's own journal, the decision
records the project declares, and the live endpoints — never a remembered
state.

## 0. Preflight (environment truth)

1. Resolve the repository's root Make diagnostic operation and declared service
   inventory. Capture failed, inactive and active states through that owner;
   raw service-manager commands do not replace its public gate.
2. Environment truth per ADR-0030: read the process's own cgroup
   (the rightmost `.service`/`.scope` segment decides).
   Inherited `INVOCATION_ID`/`SYSTEMD_EXEC_PID`/`GC_SUPERVISOR_*` are not
   evidence of unit membership.
3. If a credential-projection guard refuses an operator-session action, the
   guard is the defect when the cgroup leaf is a `.scope`; cure the guard at
   its owner. `env -u <MARKER> <command>` is a forbidden bypass.
4. In the currently authorized context, reconcile the applicable ADRs, documentation,
   selected plan, tracker and canonical skill/rule/command owners before code.
   Generation, lock resolution, provisioning and publication retain their distinct
   native operation owners; generated artifacts are not a reason for isolation.

## 1. Diagnose at the failing layer

1. Read the failing unit's journal through the declared diagnostic owner to the
   original traceback; the first exception is the failing layer.
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

1. Resolve source selection, preparation, publication and activation from the
   current project ADR and root Make surface. An explicit checkout-runtime
   authorization and an immutable-release contract are distinct; never substitute
   one for the other or infer the verb's effects from its name.
2. Use the existing transaction for its complete selected cohort. Recheck accepted
   identities before effects and prove its public second-run no-op. A source change,
   staged file or prepared receipt is not installed-runtime evidence.
3. Restart only authorized consumers whose accepted configuration, executable binding
   or declared dependencies changed. A no-op neither writes nor restarts. Prove
   sockets and consumer behavior after activation.

### Minimum-effect publication

Before activation, apply `rules/runtime/atomic-effects.md` and the project's
owning projection ADR. Resolve enabled surfaces and owned selectors from declarations.
Native adapters preserve format and validate consumers; the existing planner and
publisher compose the complete effects for each destination.

Reuse typed declaration collections and each authenticated capture/parse within the
operation; retain source/target identity rechecks. Supported entry or value changes
belong to policy data, not mirrored protocol/model properties or provider dispatch.
Generated artifacts must already meet their declared strict contracts; repair their
producer rather than appending a fixer or changing a projection.

Capture existing target bytes, ownership and metadata without treating them as source
policy. Stage only the necessary owned field, entry, block or artifact changes.
Validate each declared consumer separately and preserve foreign/manual content outside
the changed spans. Disabled capabilities must remain disabled across every producer.

Retirement requires authenticated current ownership as well as declared scope; a path,
glob, version mismatch or missing marker is insufficient. Conflicting edits, ambiguous
ownership, invalid syntax and changed source/target identities fail before publication.
Reconcile forward through the existing owner, without a competing publisher or parser.
For an explicitly authorized transaction, apply the cooperative barrier and minimal
compare-and-swap compensation contract of `rules/runtime/atomic-effects.md`.
Publication compensation does not authorize reversal of external runtime effects or
additional restarts. Retain the first causal failure and unresolved effect evidence.

## 4. Readiness evidence (activation ≠ readiness)

1. Daemon reaches its ready/healthy state with a published generation the
   remote accepted (journal lines + endpoint response captured).
2. End-to-end probes through public surfaces only (`status`, health-check,
   doctor verbs); no private method or source-text assertions.
3. Record the evidence on the tracking bead: installed release id, generation
   number, receipt digest, unit states and per-consumer behavior. Close only after
   the required integrated-source and current-SHA CI proofs as well.

## Traps (each earned in the 2026-09 campaigns)

- A test battery red under an agent shell is often the environment (inherited
  unit markers, missing generated artifacts, worktree-path substring
  collisions) — attribute before curing code.
- Exit code zero with empty output is RED.
- The dashboard port may serve HTML where the API lives elsewhere; resolve the
  management route from configuration before probing.
- Coordination surfaces (tracker store, coordinator inbox) are resolved
  through their declared owners (`direnv`, city routes), never assumed ports.
