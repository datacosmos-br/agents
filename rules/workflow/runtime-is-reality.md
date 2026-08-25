---
description: Verifying a change or claiming work done. Load when writing or fixing tests, running QA, or deciding whether a task is complete.
---

# Reality is the running system; tests are checks, not the SSOT

Validate against the real runtime (CLI, daemon, config, MCP) and manually QA the
actual feature — type and lint green are necessary, not sufficient.

- A test that only passes by keeping removed or legacy artifacts is wrong: fix or
  delete the test; never restore legacy just to make it pass.
- A config/settings test that breaks when a valid SSOT value changes is defective.
  Test contracts and derivations across arbitrary valid inputs; goldens may lock
  generated structure, never mutable config-owned values.
- A missing facade constant fails only at runtime — import and run the real path.
