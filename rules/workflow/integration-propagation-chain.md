---
description: end-to-end propagation chain from integration branch to production pilot
metadata:
  aihub.tags: '["decision:ADR-0019","effective:2026-09-11","route:personal"]'
---

# Integration propagation chain: no pilot without every hop proven

Distilled 2026-09-11 from the ai-hub model-pipeline lane (aihub-l42it) and the
flext-infra APPLY campaign (aihub-n9h36). A "production pilot" claim was being
made per-lane while the cross-repo chain had unproven hops. This rule makes the
whole chain one admissible unit.

## The chain (every hop is a gate, never a assumption)

```text
H1 integration branch GREEN      gates + tests at the merged SHA (not the PR SHA)
H2 release PUBLISHED             tag + GitHub release visible (a tag alone is not a release)
H3 consumer dependency PINNED    typed dependency owner points at H2's exact version; make setup GREEN
H4 consumer gates GREEN          check + test on the consumer at the integrated dependency pin
H5 runtime DEPLOYED              release built from integrated source; propagate verb run
H6 runtime ACTIVE                unit active AND port listening AND endpoint answering
H7 pilot CYCLE EVIDENCED         one real production cycle collected as bead evidence
```

## Invariants

1. **A hop is proven by its own command and exit, never inferred from the
   previous hop.** "PR merged" does not prove H1; "tag pushed" does not prove
   H2; "service loaded" does not prove H6 (see
   `runtime-proof-and-contract-first.md`).
2. **Version-skew gate at every binary/publisher hop.** Before H5, prove the
   publisher's pinned schema constant equals the binary's embedded constant
   (`runtime-version-skew.md`). A skew discovered at H6 costs a full diagnostic
   cycle; discovered at H5 it costs one check.
3. **Cross-repo drift is a first-class blocker.** A consumer lane (ai-hub) may
   not declare pilot readiness while its owner repo (flext-infra) has an
   integration branch ahead of its published release. Record the exact gap
   (`rev-list <tag>..<branch> --count`) on the dependent bead.
4. **The integration branch is the only landing surface.** Local unpushed
   commits on the integration branch are unfinished H1: push, re-run gates at
   the remote SHA, then proceed. Never pilot from a SHA that exists only
   locally.
5. **Propagation command text has one owner** (ADR-0028 decision 4:
   `c.AiHub.MAKE_PROPAGATE_COMMAND`). When the underlying contract changes
   (e.g. the APPLY write-enable flag is exterminated, mutation by default),
   the ADR decision that pinned the old conditional text is amended in the
   same change that lands the new contract — never left stale.
6. **Pilot admission is per `phase-admission-protocol.md`**: no open blocker
   bead in the chain, no unproven hop, evidence per step on the epic bead.

## Failure classes observed (2026-09-11)

- Pilot claimed while the consumer runtime ran a release built from a
  pre-merge branch (installed 0.4.8 from `work/wip-hier-v3` before #728
  merged) — H5 proven against the wrong source.
- Propagation verb contract described by an ADR conditional whose schema field
  (`requires_apply`) had already been dropped upstream — stale ADR text would
  have routed the next session into a nonexistent cutover.
- Release published (rc3) 255 commits behind the integration tip — H2/H3 would
  have pinned a dependency version without the landed contract.

## Owner references

- ADR-0028 (repository-local generation and runtime propagation).
- `phase-admission-protocol.md`, `production-readiness.md`,
  `landing-and-sweep-law.md`, `runtime-version-skew.md`.
- Beads: `aihub-l42it` (runtime lane), `aihub-n9h36` (APPLY extermination),
  `aihub-z82dg` (delivery contract), plan
  `.kilo/plans/2026-09-11-plan-v4-execution-proposal.md` §4 (pilot definition).
