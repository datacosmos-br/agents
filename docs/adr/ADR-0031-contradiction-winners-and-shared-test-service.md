# ADR-0031 — Contradiction winners and the shared test-service program

**Status:** Accepted **Date:** 2026-09-29 **Scope:** the rules listed under
Consequences; tracker item `ag-3l2q`

## Context

The operator's strict test program of 2026-09-29 (a product migration project and the
FLEXT libraries it consumes, workstream W1) audited this repository's rules and found
eight contradictions. The operator approved the proposed winner of each ("fix with the
proposed winners") and issued new decisions for the program: a shared host test
service, a test budget that excludes provisioning, declarative capability gating, and a
ban on operation retries. Each losing text is removed at its source; none is kept
beside its winner.

## Decision

Contradictions and their winners:

1. `flext/credential-keyring` (system Secret Service, `env-keyring auto-exec`)
   contradicted `runtime/no-keyring`, `runtime/encrypted-credential-store`, and prelude
   rule 2. It is retired; `runtime/no-keyring` absorbs its identity.
2. `flext/scanner-closure` duplicated `security/scanner-closure` with weaker semantics
   (triage files as a finding ledger; false positives without operator authorization).
   It is retired. The security rule is the one owner: triage files are evidence
   reports, and a false-positive or compatibility classification requires prior
   operator discussion, reproducible proof (for compatibility, against the declared
   language and runtime), and explicit authorization.
3. `flext/generator-declarations` point 8 ("a warning is not a failure", ADR-0024 point
   5) contradicted prelude rule 14. A warning is RED; verdict and count still derive
   from one classification.
4. `flext/managed-artifact-and-checkout-discipline` named "backup/validate/restore"
   while `storage` prohibits backups. The invocation-scoped transactional journal and
   staging used for atomic publication are recovery data of one invocation, not
   backups; persistent backups, `.bak` siblings, and archives stay prohibited.
5. `python` forbade a universal line-count threshold while
   `architecture/internal-clean-architecture`, `workflow/full-standards-conformance-sweep`
   and two skills stated 200 logical lines, and the declared FLEXT owner — the
   flext-infra `loc-cap` gate — is configured with a different ceiling. A cap exists
   only where a project declares it in its own gate; the universal layer has none, and
   no rule or skill restates the number.
6. Tool-managed instruction blocks — `rtk init` telling agents to prefix git with `rtk`,
   Beads profiles running `git pull --rebase` — contradicted "git stays plain" and the
   no-rebase law. Git stays plain; `git pull --rebase` is a rebase and is forbidden; a
   moved base, including a fork's new upstream release, is integrated with a merge
   commit. The blocks are corrected through their tools, never hand-edited.
7. The FLEXT superproject instructions made pytest coverage mandatory while
   `workflow/gate-budget` makes coverage opt-in through its own explicit target.
   Coverage stays opt-in; that text is corrected by the FLEXT superproject.
8. Prelude rule 11 differed between projections. The canonical prelude already requires
   a dedicated native worktree for every manual task and states that suspension only
   keeps orchestration inactive; stale projections are refreshed by the deploy owner.

New decisions:

9. One long-lived integration-test service per host may be shared by every checkout,
   reused while healthy, and recreated only when broken or when its declared
   fingerprint changes, under a host lock; tests isolate data in per-test namespaces.
10. The pytest budgeted phase (120 s in the FLEXT runner) excludes host-service
    provisioning, which runs in pre-test hooks, and declared `slow` tests, which run in
    their own phase with a per-item bound. Provisioning is the one fetch a test verb may
    perform — digest-pinned inputs, only when the declared fingerprint changes — so the
    offline law of `workflow/gate-budget` keeps holding for every other step.
11. Capability gating is declarative and automatic: CI never executes `remote` or
    `docker` tests; locally, `docker` tests run when the host supports Docker. A test
    that is not executed is typed and reported, never a runtime skip and never counted
    as passed; a real service failure is RED. The `NOT EXECUTED` law generalizes from
    external tokens to host capabilities.
12. The standing gate suspensions (`namespace`, `smells`) and the codemod observational
    order of 2026-09-24 remain operator decisions. Strictness comes from the active
    gates, the pytest plugins, and the project post-check; suspended and observational
    findings are still driven to zero.
13. Operation retries are banned: retry helpers such as `u.retry`, automatic
    reconnection, and `until` loops on state-changing tasks. A readiness wait is
    bounded condition polling with an explicit deadline that fails loud; it is not a
    retry.
14. A test changes the process environment only through a scoped context that restores
    it (flext-tests `u.Tests.env_vars_context`); an unrestored change fails the test,
    and `monkeypatch` stays banned.
15. An input that omits a settings key keeps its typed default; only a required value
    without a default fails. A caller that misuses the settings owner is corrected; the
    owner is not bent to it.
16. Generator-declarations point 11 (one nested class, nothing loose) does not apply to
    an executable module's `main()` entry point, `conftest.py` fixtures and hooks, or the
    dunders a generator emits.
17. Vague test rules become checkable: a project-owned value is one declared by a
    configuration, settings, or constants owner, while synthetic fixture inputs are
    scenario data; a bare `assert` is allowed only where no flext-tests `tm` matcher
    expresses the check.
18. The Portuguese texts of `workflow/mass-rewrite-discipline` (templates section),
    `coordination/fleet-landing-corrections`, and the description of
    `workflow/discovery-before-decision` are translated; the universal home is
    English-only. The translated templates section names the root test verb instead of
    a raw `pytest` invocation.

## Consequences

- Retired: `rules/flext/credential-keyring.md` and `rules/flext/scanner-closure.md`;
  their survivors record the supersession in their bodies.
- Amended under this record: `architecture/engineering-core`,
  `architecture/internal-clean-architecture`, `coordination/fleet-landing-corrections`,
  `flext/generator-declarations`, `flext/managed-artifact-and-checkout-discipline`,
  `git/destructive-git-guard`, `git/fork-version-locality`, `python`,
  `python/config-settings-ssot`, `runtime/no-fallback`, `runtime/no-keyring`,
  `security/scanner-closure`, `testing/observable-runtime`, `workflow/gate-budget`,
  `workflow/generators-not-projections`, `workflow/full-standards-conformance-sweep`,
  and `workflow/mass-rewrite-discipline`. `flext/gate-registry-ownership` rewires its
  reference to the surviving scanner rule. The FLEXT development and Pydantic skill
  references defer the module cap to the `loc-cap` gate, and the verification-loop
  procedure records capability-gated tests as typed `NOT EXECUTED`.
- [ADR-0024](ADR-0024-flext-generator-declarations.md) point 5 (warning verdict) is
  replaced by decision 3, and its facade-module point gains the carve-outs of decision
  16.
- Owners outside this repository: the FLEXT superproject instructions (coverage clause,
  RTK and Beads blocks), the AI Hub instructions (RTK and Beads blocks), the Beads fork
  agent templates and doctor hints (`git pull --rebase`), and the AI Hub home and
  project projections that still carry the retired prelude rule 11 wording.
- AI Hub consumes the released bundle and owns deployment; source edits or a green
  package load alone do not prove propagation.
