---
name: web-guidelines
description: 'ui review, interface guidelines, accessibility audit, ux compliance'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0014","effective:2026-09-07","usage:on-demand"]'
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## Provenance

- Origin: <https://github.com/vercel-labs/agent-skills> (`web-design-guidelines`)
- Commit: `f8a72b9603728bb92a217a879b7e62e43ad76c81`
- License: MIT

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```text
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:

1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.
