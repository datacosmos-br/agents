# ADR-0010: Optional host runtime boundary

## Status

Accepted — 2026-09-05

## Context

Portable libraries need to work in repositories and CI environments where the operator's
runtime control plane is not installed. Moving host automation into those libraries
creates a reverse dependency, duplicates runtime state, and turns an optional developer
capability into a package requirement. Treating an absent host as an error is equally
incorrect; silently replacing a selected, failing host hides the real failure.

## Decision

1. Portable libraries own standalone primitives only. Host-wide indexes, daemons, forge
   clients, LSP/refactor orchestration, hooks, and MCP belong to the runtime control
   plane that operates them.
2. A library may consume an installed host capability only through a public command,
   hook, or MCP contract. It never imports or links the host application as a library
   and never reads or produces the host's private state.
3. An absent and unselected optional host capability is not an error and creates no
   substitute path. Once explicitly selected and available, its first error propagates
   without retry, fallback, or normalization.
4. In FLEXT, `flext-infra` owns Git primitives and static `.github` codegen; `ai-hub`
   owns live GitHub operations plus CRG index production and host CRG/LSP/Rope
   automation.

## Consequences

FLEXT projects remain fully operable without ai-hub. An installed ai-hub may augment
them through stable process boundaries while retaining sole ownership of its daemons,
indexes, credentials, and forge integrations. The same rule applies to future host
runtimes without introducing a dependency from reusable libraries back to the operator
environment.

## Approval

Operator directive, 2026-09-05: flext-infra may use ai-hub commands, hooks, MCP,
runtime, and daemons when available, never ai-hub as a library; absence must not fail,
Git stays in flext-infra, and GitHub plus CRG index production stay in ai-hub.
