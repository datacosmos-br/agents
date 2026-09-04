---
description: Test observable runtime behavior
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-30","route:both"]'
---

# Test observable runtime behavior

Tests validate what the public module does. Do not mock, assert private methods,
ignore violations, aggregate defects, or freeze implementation shape. Prove
that raw exceptions, causes, child failures, and pre-effect validation escape
through the public surface. Runtime is reality; fix a defective test instead of
restoring incorrect or legacy production behavior.

A unit test opens no network socket and writes nowhere outside its `tmp_path`
fixture. Fixtures provision the contract under test — credential store, git
remotes, service endpoints — physically inside that sandbox; a test proves
behavior against the fixture, never against a real remote. A test that
reaches outside the sandbox (a `git ls-remote` against a real remote, an
unstubbed HTTP call, a write to the repository tree or the real home
directory) is a test defect at its owner, never an accepted skip, xfail, or
network-dependent marker.

See also: `runtime-is-reality.md` (rule file) — runtime-first contract.
