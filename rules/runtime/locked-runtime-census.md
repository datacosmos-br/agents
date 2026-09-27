---
description: Census and debt maps are evidence only when the executing runtime matches the lock.
metadata:
  aihub.tags: '["decision:ADR-0028","effective:2026-09-27","route:both"]'
---

# Census validity requires the locked runtime

Before computing, triaging, decomposing, or recording any census, smell, or
enforcement finding, verify that the installed runtime equals the lock
resolution. For a Git dependency this is the `vcs_info.commit_id` in the
installed distribution's `direct_url.json` versus the `#<commit>` fragment
resolved for it in `uv.lock`. On mismatch the map is void: sync through the
repository's declared upgrade verb, recompute, and only then plan.

A debt map measured against a stale runtime is retired, not repaired. Any
record of census state travels with three facts — the findings count, the
executing scanner's commit, and the lock's resolved commit; a record missing
one of them is not evidence of debt. Decomposition work planned from a
pre-sync map must not execute until the re-measurement reproduces the finding
on the locked runtime.

Provenance: flext-infra PR #947 carried an 87-finding census decomposition
plan that proved to be an artifact of a venv installed two scanner generations
behind the lock; after sync and base alignment the same gate reported zero.

See also: `preflight-before-effects.md` (rule file) — validate before any
effect; `fail-loud.md` (rule file) — a mismatched runtime stops the workflow.
