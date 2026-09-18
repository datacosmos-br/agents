---
name: agent-browser
description: "browser automation, web interaction, agent-browser"
allowed-tools: Bash(agent-browser:*)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:agent-browser","effective:2026-08-28","route:agent","subject:agent-browser","usage:on-demand"]'
---

# agent-browser

Activate only for an explicit browser interaction or browser-produced artifact. A
source-only review, copied page text, or ordinary HTTP request does not activate this
skill.

## Contract

1. Before opening a page or changing browser state, resolve the exact target origin,
   installed `agent-browser` interface, browser/provider, session isolation, proxy,
   required current-process credentials, allowed effects, expected observable result,
   and final artifact destinations. Reject any missing, invalid, conflicting, or
   unexpanded requirement.
2. Use only the selected interface and execution path. Do not use aliases, saved
   profiles, persisted authentication state, keyring, credential files, provider or
   proxy rotation, auto-executing templates, or an alternate browser.
3. Observe the current page and take a fresh interactive snapshot before every ref-based
   action. Navigation or a material DOM change invalidates prior refs; re-snapshot
   before continuing. Never invent a selector or ref.
4. Complete all preflight checks before click, fill, upload, submit, cookie, storage,
   network, download, recording, or publication effects. Wait for an exact observable
   condition; arbitrary sleeps and retries are prohibited.
5. Verify the rendered result and requested artifacts. Publish each artifact only after
   validation, atomically at its declared destination.
6. The first command, timeout, signal, page, assertion, or publication failure ends
   execution with its causal output unchanged. Cleanup may attach its own failure, but
   must re-raise the first cause and remove partial artifacts.

Report the observed result and durable artifact paths. Never claim an action or artifact
that was not observed.
