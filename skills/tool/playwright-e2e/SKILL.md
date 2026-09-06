---
name: playwright-e2e
description: 'playwright, end-to-end testing, browser fixtures'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:dependency:npm:@playwright/test","detect:dependency:npm:playwright","effective:2026-08-28","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","tool:playwright","updates:manual","usage:on-demand"]'
---

# Playwright E2E

Activate only for observable browser behavior in a project with a detected
Playwright dependency. Pure logic and known non-browser boundaries stay in the
project's narrower test owner.

Before browser or server effects, read the pinned dependency and current project
configuration, test environment identity, base URL, routes, selectors, network
contract, user state, fixture data, expected outcomes, effect authorization,
required current-process credentials, and final artifact destinations. Reject
missing or unsafe targets; never assume localhost, timing, browsers, CI, auth,
data, retries, or configuration.

Implement the smallest project-native test that proves the requested visible
behavior. Use declared semantic locators and exact observable conditions; do not
sleep, retry, skip, quarantine, catch failures, or add a page object, reporter,
browser matrix, mock, or artifact the project does not require. Effectful flows
run only in an isolated authorized environment and complete preflight before the
first effect.

The first Playwright, server, assertion, timeout, signal, or child failure
propagates unchanged. Validate requested screenshots/traces before atomic
publication. Cleanup may attach a secondary failure but must re-raise the first
cause and remove partial browser, server, data, and artifact residue.
