---
name: conformance-sweep
description: Execute one zero-residue conformance sweep cycle (governance repair, idempotency, budget, coordination) end-to-end with beads and landing gates.
argument-hint: "<scope: repo or workspace, e.g. flext-infra>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:project"]'
---

# Conformance sweep

Treat `$ARGUMENTS` as the sweep scope (one repo or the superproject). Refuse an
empty argument.

1. **Resolve authority**: root `AGENTS.md` -> branch-matched `flext-law` ->
   nearest scoped `AGENTS.md` -> the active bead. Read the living plan under
   `docs/plans/` for this sweep if it exists; continue it, do not fork it.
2. **Open the governance bead first** (before any mutation): one hotfix bead
   describing the delta with exact SHAs, plus one bead per discovered red with
   failing site, hypothesis, and trigger. Every later step records evidence
   there.
3. **Inventory before discard/rewrite**: any history surgery requires the
   hunk inventory per `rules/workflow/landing-and-sweep-law.md`; classify each
   hunk as re-derived, port-back-needed, or superseded — in the bead.
4. **Idempotency gate** (generation surface): `make gen` twice;
   artifacts to `/tmp/fixed-point/`; `difflib.unified_diff` written to a file
   (code­gen stdout is flooded — never read diffs from console flow). On
   divergence: hypotheses H1 tooling determinism (taplo/uv resolve), H2
   post-publish writer block, H3 stale registry; fix at the block's writer;
   add the convergence regression test.
5. **Budget check**: run the affected test files; every non-slow test must
   stay within 10s. A test doing real provisioning in-line is rewritten to
   fixture + receipt assertion — never raise the limit.
6. **Close with landing**: lane branch -> PR -> review -> `--no-ff` merge ->
   gates rerun on the merged SHA -> close beads with the four-evidence pattern
   (recorded state, git history, measured reality, integrated code). A local
   green or an open PR is never a landed state.
7. **Persist the lessons**: `bd remember` for each new durable law found
   during the sweep; extend the affected `~/agents/skills` if a failure mode
   was procedural rather than situational.
