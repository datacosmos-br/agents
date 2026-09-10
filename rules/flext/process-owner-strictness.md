---
description: process-owner strictness contracts
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:personal"]'
---

# Process-owner strictness contracts

Two failure classes observed 2026-09-10 (aihub-l42it lane). Both are invariants:
fix at the owner, never add a caller-side workaround.

## Git's legal exit-1 must not trip stderr-strict owners

The fleet process owner treats any stderr payload as a typed failure. Several
git probes have DOCUMENTED non-zero exits that also write to stderr on legal
states. Probing such commands without silencing stderr converts a legal state
into a hard failure (observed: `git symbolic-ref refs/remotes/origin/HEAD`
exit-1 "not a symbolic ref" broke every originless/detached checkout in
wip-hier).

Rule: when a git probe has a documented code-level absence contract, invoke it
with `--quiet` (or an equivalent stderr-silent form) and read the absence from
the return code. Every other failure propagates raw. Pair each such probe with
one regression test that constructs the legal-absence repo (a plain `git init`
checkout has no origin/HEAD).

## Boundary JSON ingress rejects duplicate keys

`json.loads` (and Pydantic `model_validate_json`) silently apply
last-key-wins. An external source boundary that must fail closed on corrupted
payloads needs `object_pairs_hook` raising on duplicate keys, wired AT the
boundary adapter that declares the ingress contract. Declaring the hook
function without wiring it into the parse call is dead code (observed:
`reject_duplicate_source_json_keys`). If the fleet JSON primitive grows a
strict mode, migrate the boundary to it and delete the local hook in the same
change.
