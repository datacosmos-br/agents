---
description: A declared fleet tool owns its job; code that reimplements it is the defect
metadata:
  aihub.tags: '["decision:ADR-0026","effective:2026-09-24","route:both"]'
---

# A declared fleet tool owns its job; reimplementing it is the defect

A tool that the toolchain installs and the project declares owns the job it does. When
it is installed and nothing calls it, the defect is not its absence — it was unwired, and
the code that grew in its place is the violation.

## How the damage shows

A reimplementation does not fail at once. It works, and it erodes what the original tool
protected:

- **The lineage the tool reads breaks.** Writing a value the tool owns (a version, a tag)
  locally diverges the state it reads to decide what changed, and its selection silently
  degrades to "everything".
- **A cascade grows to cover the break.** Something must then rewrite every dependent on
  each run, so one change recreates the whole set.
- **Parallel caches grow**, often keyed on the tool's own cache.
- **The reimplementation's defects are attributed to the tool.** A limit blamed on the
  tool turns out, measured against the tool alone, to be produced by the local staging.

## Requirements

- Before writing a mechanism, check whether the toolchain already installs one (`which
  <tool>`, the version manager's registry). One command answers it.
- An unwired tool is reported as a defect and rewired; it is never replaced by local code.
- A limit, error or behaviour attributed to an external tool is measured against that
  tool in isolation before it justifies workaround code. A workaround built on unmeasured
  behaviour tends to become a workaround for the workaround.
- When the tool is rewired, all code that redid its job leaves in the same cutover, with
  its tests, verbs, constants, documentation and the decisions that authorised it. One
  active residue reopens the route.
- A supersession note that asserts operator authorisation is verified with the operator
  before it is treated as authority. It is the one class of claim an agent cannot
  self-certify.

## Enforcement

The permission dies with the hack: the document that names the replacement as owner — an
ownership matrix, an ADR, a runbook — is corrected in the same cutover. While it names the
replacement, the next session rebuilds it in good faith.

Compose with `generators not projections` (rule file), `zero residue` (rule file) and
`safe delete` (skill), which owns the atomic cutover contract.
