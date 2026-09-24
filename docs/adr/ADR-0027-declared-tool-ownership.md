# ADR-0027 — A declared fleet tool owns its job; reimplementing it is the defect

**Status:** Accepted **Date:** 2026-09-24 **Scope:**
`rules/workflow/declared-tool-ownership.md`

## Context

On 2026-09-23 the operator stated that the removal of `helm-semver` from the
`cosmos-charts` release flow had never been authorised. Measurement confirmed the tool
had never left the machine: it was installed in the fleet toolchain
(`mise/shims/helm-semver`, fork `marlon-costa-dc/helm-semver`) and simply no longer
called. Roughly 2900 lines had grown in its place, redoing by hand what it does from
conventional commits — versioning, packaging, registry push, tagging and releasing.

The replacement did not fail at once. It worked, and it eroded what the tool had
protected:

- **The lineage the tool reads broke.** Writing `version:` locally diverged the tags it
  uses to decide what changed: `aligned=0, drifted=78`. Per-chart selection silently
  degraded to "every chart".
- **A cascade grew to cover the break.** With consumers pinning owners exactly and owner
  versions rewritten locally, a step had to rewrite every consumer's pin on each run, so
  one chart recreated the fleet.
- **A parallel cache grew.** A content-addressed cache wrapped `helm dependency build`,
  keyed on a hash it built by reading Helm's own cache.
- **The replacement's defects were attributed to the tool.** A 100 MiB ceiling was
  blamed on Helm. Measured with plain Helm on the chart that hit it: 376 KB, clean
  package. The nesting came from the local staging.

The removal had been recorded in an ADR note that asserted operator authorisation. The
operator states that authorisation never existed. A claim of operator authorisation is
the one class of claim an agent cannot self-certify.

## Decision

1. A tool the toolchain installs and the project declares owns the job it does. When it
   is installed and nothing calls it, the defect is that it was unwired, and code grown in
   its place is the violation to remove.
2. Before writing a mechanism, check whether the toolchain already installs one.
3. A limit, error or behaviour attributed to an external tool is measured against that
   tool in isolation before it justifies workaround code.
4. When the tool is rewired, everything that redid its job leaves in the same cutover —
   tests, verbs, constants, documentation, and the decisions that authorised it.
5. A supersession note that asserts operator authorisation is verified with the operator
   before it is treated as authority.

The rule text is `rules/workflow/declared-tool-ownership.md`.

## Consequences

- The document that names the replacement as owner is corrected in the same cutover; a
  surviving ownership matrix or runbook lets the next session rebuild the replacement in
  good faith.
- The `cosmos-charts` instance is recorded in `cosmos-main` ADR-147 and bead
  `cosmos-53gsc`.
