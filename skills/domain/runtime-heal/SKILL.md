---
name: runtime-heal
description:
  "runtime service recovery, failure diagnosis, installed-release activation, readiness"
license: MIT
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0030","detect:opt-in:runtime-heal","effective:2026-09-27","route:project","subject:deployment","usage:on-demand"]'
---

# Runtime heal

Recover a failed runtime service to proven readiness: diagnose at the failing
layer, cure the owner the traceback names, and close only with command
evidence that the service is serving — activation alone is never readiness.

Read `references/procedure.md` before any effect. The procedure owns the
ordered checklist (states, contracts, evidence commands, traps): service unit
triage, snapshot/publication contracts, compare-and-swap publication,
development-versus-production activation contracts, credential-projection
guard interplay, and idempotent-install proof. Every step ends in a captured
command; a step without captured output did not happen.

A failure is cured at the owner the traceback names — never suppressed,
retried, bypassed, or normalized; an inherited environment marker is never
evidence of process context (ADR-0030). Compose with `deploy-lifecycle` when
the cure lands through a release, and with `$deploy-lifecycle` acceptance
before declaring the fleet healthy.
