---
description: runtime proof beats unit state; contract-first diagnosis
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:personal"]'
---

# Runtime proof and contract-first diagnosis

Two diagnostic invariants distilled 2026-09-11 (aihub-l42it model pipeline lane). Both
are invariants, not preferences.

## A systemd unit reporting active is not runtime proof

A `Type=forking` unit that detaches its daemon reports `active (exited)` while the
actual process is dead (measured: `ccs-cliproxy.service` active for 6h with port 8317
empty and the pipeline daemon failing on 502 downstream). The unit state describes
supervision bookkeeping, not the service.

Rule: for any network daemon, runtime proof = listener present (`ss -tln | grep <port>`)
AND one real endpoint response with expected payload shape. Only then continue dependent
work. If a unit can report active while the service is dead, file the supervision defect
at the unit owner — do not adopt `is-active` as a gate.

## Diff fields before comparing blobs

When a canonical-JSON comparison fails (CAS 409, digest mismatch, "stale facts"), do not
iterate on whole-blob diffs. Diff keys field-by-field at each nesting level first:

```bash
python3 - << 'EOF'
import json
a = json.load(open('snapshot.json')); b = json.load(open('live.json'))
def walk(x, y, p=''):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in set(x) | set(y):
            walk(x.get(k), y.get(k), f'{p}.{k}')
    elif x != y:
        print(f'{p}: snapshot={x!r} live={y!r}')
walk(a, b)
EOF
```

One flipped field (`active: true→false`) identified in a single read beats three rounds
of blob archaeology.

## Map every assert in the chain before touching the first one

A publication chain with 11 asserts (identity, CAS subset, generation, parse, schema
minItems, credential subset, readback digests) behaves like a series circuit: fixing
assert N only surfaces assert N+1. Before the first fix, list every assert with its
owner and failure class (race / state / content / bug), then predict which failure the
fix will displace the symptom to. If the prediction is wrong, the mental model is wrong
— stop and re-map.

Owner references: session bead and tracker for the assert map, chain asserts, and unit
defect respectively.

## Runtime is the acceptance authority (operator, 2026-09-27)

Tests verify the consumer contract; they do not define it. When a test's premise
contradicts observed runtime behavior, the test is rewritten in the same commit as
the contract change — never the runtime contorted to satisfy the test, and never
the suite waved green while the runtime stays broken. The full rule lives in
`rules/workflow/runtime-first-contract-tests.md`; this section is the cross-reference
that binds it to the contract-first diagnosis above (diagnose on the runtime, fix at
the owner, reconcile the tests, all in one commit).
