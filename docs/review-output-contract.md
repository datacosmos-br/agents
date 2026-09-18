# Shared Review Output Contract

Apply this contract only when a reviewer explicitly selects one of its approval
policies. Preserve the reviewer's language-specific diagnostic commands and framework
checks at their existing owners.

## Issue entry

```text
[SEVERITY] Issue title
File: path/to/source.<ext>:42
Issue: The concrete defect and its consequence.
Fix: The required change.
```

## Review summary

End every review with this table and a verdict derived from the selected policy:

```text
## Review Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 0     | pass   |
| HIGH     | 1     | block  |
| MEDIUM   | 2     | info   |
| LOW      | 0     | note   |

Verdict: BLOCK — HIGH issues must be fixed before merge.
```

## Approval policies

- **medium-caution**: approve with no CRITICAL or HIGH findings; report a caution when
  only MEDIUM findings remain; block on any CRITICAL or HIGH finding.
- **high-blocking**: approve only with no CRITICAL or HIGH findings; block on any
  CRITICAL or HIGH finding.

A project-owned reviewer may add required automated checks to its blocking condition,
but it may not weaken either policy.
