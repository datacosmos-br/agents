# Workflow: feature

## Goal

Deliver one complete capability through its canonical owner, all consumers,
runtime proof, native gates, review, and integration.

## Procedure

1. Read repository law, architecture, relevant decisions/docs, owners,
   consumers, Git state, and concurrent WIP.
2. Confirm the requested public contract and exclusions. A new unapproved
   interface or materially different scope stops for one precise operator
   decision.
3. Discover the repository's canonical commands through `make help` or its
   declared equivalent.
4. Observe the nearest existing runtime behavior and reuse the owning facade or
   primitive.
5. Define observable acceptance scenarios, including failure and
   should-not-trigger behavior where applicable.
6. Implement the smallest complete vertical slice. Parse external input once
   into typed boundaries; update all consumers and delete superseded paths.
7. Run the actual feature through its public runtime before adapting tests.
8. Run affected native lint, format, type, test, build, security,
   documentation, and generation/fixed-point gates.
9. Repeat short slices until the approved capability is complete; never start a
   later slice over a red earlier slice.
10. Follow the landing contract in [WORKFLOWS.md](WORKFLOWS.md).

## Fail-closed rules

- No prototype, stub, TODO, compatibility layer, fallback, alternate model,
  suppression, or deferred cleanup may land.
- A missing tool, warning, skipped gate, auth/quota failure, or review thread is
  red.
- Do not mutate another repository or project projection unless it is explicitly
  in scope and independently authorized.
- While tracker runtime is suspended, create no substitute tracker or ledger,
  preserve evidence only in separately authorized Git/PR/CI, and leave phase
  closure open.
