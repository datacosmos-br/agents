---
description: Verify runtime reality before tests or completion claims
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
---

# Reality is the running system; tests are checks, not the SSOT

First reproduce and validate the declared public import, API, CLI, daemon,
service, generated consumer, deployed artifact, or other real runtime selected
by the project. Verify its revision or release identity. Only after that
contract is measured may tests be created, adapted, or invoked. An editable
checkout, test assertion, snapshot, local cache, generated copy, or stale
environment does not define runtime behavior.

- A test that only passes by keeping removed or legacy artifacts is wrong: fix or
  delete the test; never restore legacy just to make it pass.
- A config/settings test that breaks when a valid SSOT value changes is defective.
  Test contracts and derivations across arbitrary valid inputs; goldens may lock
  generated structure, never mutable config-owned values.
- A missing facade constant fails only at runtime — import and run the real path.
- A test run that executes zero tests is not evidence, whatever its exit code.
  Impact selection (testmon) that does not select the test of the change
  (`3 deselected / 0 selected`, or a template/Makefile edit no Python test
  claims) and a runner that reports `no tests ran` with exit 0 after a
  collection error are both false greens: name the test that asserts the
  change and prove it ran.
- Before concluding root cause, prove the running or installed artifact matches
  the declared authoritative revision or release. An editable checkout, local
  cache, generated copy, or stale environment is not evidence of remote/runtime
  behavior until identity is verified.
- Use the newest released version of every required tool. Every diagnostic it
  emits is blocking. A cap, downgrade, substitution, suppression, compatibility
  classification, or false-positive classification requires prior operator
  discussion, reproducible evidence, and explicit authorization; without all
  three, correct the owner and rerun that released version.
