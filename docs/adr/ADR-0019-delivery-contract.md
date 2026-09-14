# ADR-0019 — Delivery contract: typed capsule budget, lifecycle events, and linking gates

**Status:** Accepted
**Date:** 2026-09-10
**Scope:** `src/agents_governance/delivery.py`, `config/governance.json`, `tools/check_docs_links.py`, `Makefile`, `.gitignore`
**Evidence:** measured capsule compositions on 2026-09-10 (beads ag-p4a.6/.8)

## Context

The session capsule is delivered as provider hook output, which truncates at
10,000 characters. The 2026-09-10 audit measured the always-on composition
(prelude + bootstrap rule summaries + skills router index) at 9,764 characters
— inside the ceiling with only 236 characters of headroom and no gate to
enforce it: every future bootstrap addition risked silent truncation, which is
the distribution failure mode observed in production sessions. The same audit
found the delivery semantics (which payload each lifecycle event carries)
expressed only as prose, and the documentation link grammar (ADR index,
relative links) unenforced.

## Decision

1. **Typed delivery contract** (`config/governance.json` `delivery` section,
   parsed into `DeliveryContract`): a grammar-validated event map — any
   sorted slug event keys, each carrying sorted unique `payload:<slug>`
   components — plus `capsule_budget_chars = 10000` and
   `restore_list_reserve_chars = 512` for the compaction restore list the
   runtime appends after compaction. Config owns the instances; code
   validates structure only. Fixed instance vocabularies in code are a
   bypass and are prohibited (operator correction, 2026-09-10): future
   events and payloads are config data, never code changes.
2. **Budget gate at load** (`audit_delivery`): `GovernanceBundle.load()`
   measures the exact always-on composition and raises with the full
   breakdown when prelude + bootstrap rule summaries + bootstrap skill index
   exceeds `budget − reserve`. Silence proves fit; the measured numbers are
   exposed on the bundle snapshot.
3. **Docs linking gate** (`tools/check_docs_links.py`, wired into
   `make docs`): the ADR index table is a bijection with physical ADR files,
   and every relative Markdown link under `docs/` resolves. Stdlib-only so
   CI runs it bare.
4. **Marker reconciliation**: `.gitignore` names the canonical
   `managed-by` + version marker contract (ADR-0015) for materialized
   provider paths, replacing the ambiguous "AI Hub owner marker" wording.
5. **Absorbed and closed**: the `.kilo` gap-plan Task 3 (agent approval
   lineage in `_approved_artifacts` and `resolve_approval_tags`) was measured
   as already implemented in the current code; the plan record is corrected,
   and no parallel implementation is created.

## Consequences

- Bootstrap changes that overflow the capsule now fail at load with measured
  numbers instead of truncating silently in production sessions.
- The AI Hub runtime consumes the validated event map and budget from the
  bundle (ADR-0008 boundary); it never re-derives them from prose.
- Summary prose becomes a maintained budget surface: growth requires
  mediation in the same change, visible in the gate failure.
