---
description: Tests confirm observed runtime behavior through public interfaces
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Observable tests

Expected results come from the public contract, never from the code under test, and
configuration-owned values are read from their owner, never frozen. A mock, patch, fake,
private access or implementation assertion is replaced by public behavioral coverage of
the same failure scenarios, or removed. Unit tests open no socket, write only inside
fixture storage and restore any environment they change. A red test is fixed at its
contract, never by weaker assertions, xfail or lower coverage. Warnings, zero
collection, a missing tool or report, and a selected suite that did not run are red; a
skip is red unless it is the project's declared availability prerequisite, reported as
unmet. A shared integration service is one host instance provisioned before the test
clock, with a namespace per test; the rest is the [law](../law.md).
