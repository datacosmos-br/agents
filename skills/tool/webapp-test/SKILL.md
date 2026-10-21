---
name: webapp-test
description: "playwright, login flow, console errors, local webapp"
license: Apache-2.0
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:playwright","effective:2026-09-07","extends:playwright-e2e","route:project","subject:playwright","subject:web","usage:on-demand"]'
---

# Local web application testing

Compose $playwright-e2e and resolve the current application's public behavior,
authentication boundary, native test command and browser ownership first.
Use that project command for execution; a bundled script is not a substitute
for its guards, runtime or acceptance evidence.

Inspect the DOM before choosing selectors, wait for observable readiness and
exercise the real user flow. Preserve console errors and failed requests.
Snapshots and a successful page load alone do not prove the changed behavior.
Use these examples as references, not copied project infrastructure:

- [Console capture](examples/console_logging.py)
- [Element discovery](examples/element_discovery.py)
- [Static HTML](examples/static_html_automation.py)

## Server helper boundary

The public helper is [with_server.py](scripts/with_server.py). Read its declared
help and source when auditing or diagnosing it; no instruction forbids source
inspection. Its required contract is exact argv/cwd preservation, visible streams,
bounded readiness and cleanup of owned processes on failures and termination.
Shell expansion and another framework runtime are not required to execute argv.

Implementation pending: the current helper and the reviewed async replacement
must pass that public lifecycle contract, including signals and descendants,
before any cleanup guarantee is claimed. Preserve the existing source work and
repair this helper's author; do not create a second runner in the application.
The selected task carries the current migration evidence and disposition.

## Provenance

- Origin: <https://github.com/ComposioHQ/awesome-claude-skills> (`webapp-testing`)
- Commit: `92568c1edaff1bde5371154f036d959346c145a8`
- License: Apache-2.0
