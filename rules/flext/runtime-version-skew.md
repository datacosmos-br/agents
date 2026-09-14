---
description: runtime version-skew detection between publishers and binaries
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:personal"]'
---

# Runtime version-skew: prove the pair before any redeploy

Failure class observed 2026-09-11 (aihub-l42it, model pipeline): a compiled
dist was redeployed from source pinned at schema version 3 while the installed
binary still enforced version 2 (`model-routing v2 is required`). The skew was
introduced BY the redeploy and cost a full diagnostic cycle.

## Invariants

1. **Never redeploy a publisher/binary pair without proving both sides of the
   version contract first.** For a binary, read the constant from its own
   provenance: `--version`, embedded strings, or the management endpoint that
   echoes the schema version. For a publisher, read the pinned constant in its
   source AND in the deployed dist artifact (they can differ after a partial
   copy).
2. **The pair, not the artifact, is the unit of deployment.** A dist copied
   from source at HEAD is not "the same version" as the previously installed
   dist — it is a new deployment that must re-prove compatibility with every
   peer it talks to.
3. **Skew must fail typed at the first call, not as an opaque downstream
   error.** If the owner cannot yet emit a typed skew error, the diagnostic
   path is: read both versions → name both with commit provenance → then fix.
4. **Upgrade direction is chosen by the contract owner, not by convenience.**
   When source pins N and the binary accepts N-1, prefer upgrading the binary
   if a build with N exists (owner published the intent); downgrading source is
   a contract rollback requiring explicit operator approval.

## Diagnostic pattern (measured, 2026-09-11)

```bash
# binary side: provenance + embedded schema marker
<binary> --version
strings <binary> | grep -oE '<schema error strings>' | sort -u
# publisher side: source constant AND deployed dist constant
grep -rn '<SCHEMA_VERSION_CONST>' <src>/…/<types>.ts
grep -rn '<SCHEMA_VERSION_CONST>' <dist>/…/<types>.js
```

If they disagree, the redeploy is the regression — stop and reconcile before
any other hypothesis.

## Owner references

- ai-hub model pipeline: `aihub-37x3e`, plan
  `.kilo/plans/2026-09-11-status-review-plan.md` §5-W3 (typed skew gate).
- CCS pins: `src/config/schemas/model-pipeline-types.ts`
  (`CLIPROXY_MODEL_ROUTING_SCHEMA_VERSION`); binary truth:
  `internal/modelrouting/schema.go` (`SchemaVersion`).
