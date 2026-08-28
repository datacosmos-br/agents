# Session protocol

## Start

1. Read this package in its declared order and the active repository runbook.
2. Confirm the newest operator instructions and repository law; reconcile any
   contradiction before implementation.
3. Inspect current files, owners, consumers, generated markers, provider
   capabilities, dirty state, and active processes without invoking suspended
   runtimes or Git unless separately authorized.
4. Identify the current phase and verify every predecessor exit condition.
5. Use only the documented optionless `agentsctl` runtime verbs; run `make help`
   only to discover development and gate-composition targets.
6. Build one search-first evidence packet: canonical owner, affected consumers,
   runtime surface, current tests, provider formats, and native gates.
7. When tracking is suspended, create no substitute state store and preserve
   proof only in separately authorized Git/PR/CI.

## Work cycle

For each cohesive owner change:

1. apply YAGNI and remove unrequired scope;
2. elect one SSOT and classify projections;
3. check SOLID boundaries where architecture changes;
4. implement through the owner and simplify inline;
5. use DRY only for proven semantic duplication, then recheck YAGNI/SSOT/SOLID;
6. run the representative public `agentsctl` verb with no options;
7. run focused tests and contradiction search;
8. run broader gates required at the phase boundary.

After an operator correction, immediately search for both the new rule and its
semantic opposite, update canonical owners, and remove the opposite. While the
tracker is suspended, create no substitute tracker or ledger and preserve
evidence only in separately authorized Git/PR/CI surfaces.

## Concurrent work

- Treat existing dirty changes as owned input; never discard or overwrite them.
- Attribute each retained hunk to a current contract.
- If another actor changes the same owner, compare intent and preserve both
  compatible changes. Stop on a real contract conflict.
- Do not create another checkout to avoid coordination.
- Do not regenerate an entire tree over unattributed content.

## Blocking handoff

A handoff is permitted only when the operator pauses/reorders the phase or the
remaining condition is external and every authorized technical correction is
exhausted. A red check, actionable review finding, open PR, or pending merge is
otherwise an instruction to keep correcting and revalidating the same phase.

Report:

```text
repository and phase
exact command or attempted operation
working directory
exit code
decisive error
canonical owner that must change
files intentionally changed
runtime and gates already passed
unresolved authority or external condition
next safe action
```

Do not propose an alternate tracker, model, server, provider type, retry,
fallback, suppression, compatibility route, fake projection, keyring, error
normalization, or destructive cleanup.

## Phase handoff

A new session must be able to determine from canonical source and authorized
Git/PR/CI evidence:

- current phase and integration SHA;
- source and target artifact counts derived by discovery;
- owner changes and removed competitors;
- runtime commands with exit codes and decisive output;
- Waza scenario and provider-adapter results;
- projection fixed-point result;
- review/check state;
- exact blocker or next owner-level action.

Do not trust green evidence from another SHA, environment, provider version, or
model. Revalidate affected behavior after integration changes.

## End

An unfinished session leaves the existing checkout and foreign destination
content intact. A landed session cleans only attributable, reachable residue.
Neither case reports `DONE` while canonical tracker closure is unavailable.
