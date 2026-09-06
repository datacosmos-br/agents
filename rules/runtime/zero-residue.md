---
description: Atomic cutover and extermination of every superseded contract.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","route:both"]'
---

# A cutover leaves zero active residue

In the same coherent change, rewire every current consumer and delete every
superseded implementation, entry point, option, alias, configuration key,
generated projection, test, fixture, document, and dependency. Do not retain a
shim, compatibility reader, TODO, deprecation window, old/new coexistence, or
follow-up cleanup item. Do not move residue into a backup, archive, retirement,
quarantine, `.bak`, or hidden sibling; after proven rewire, delete it.

Search semantic and textual opposites across source, configuration, tests,
docs, evals, build/CI owners, manifests, and generated artifacts. Any active
opposite blocks landing. Historical Git and evidence records remain truthful
history; they are not runtime residue or rollback authority.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
