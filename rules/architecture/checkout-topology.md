---
description: Project kind decides who may rewrite a repository; topology is workspace or standalone, never a third value.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-06","route:both","supersedes:rule:architecture/project-kind-and-checkout-topology"]'
---

# Project kind gates generation; topology has exactly two values

Two orthogonal facts describe a repository, and confusing them has already cost
this fleet a fabricated vocabulary and thirty prohibited symlinks.

## Kind decides treatment

Every repository is exactly one kind, and the kind is declared, never inferred
from a path, a name, or the presence of a dependency:

- `internal_flext` — an owned project built on the FLEXT platform.
- `internal` — an owned project that is not FLEXT.
- `third_party_fork` — a fork of someone else's project.

A generator, standardizer, conformer, or modernizer may rewrite only
`internal_flext` repositories. An `internal` project receives no FLEXT layout,
facade chain, typing policy, or generated interface, because those are FLEXT
law and it is not a FLEXT project. A `third_party_fork` follows its upstream in
everything — layout, language level, style, build, tests, architecture — and
local governance owns only source identity, delta provenance, artifact
integrity, deployment configuration, and runtime proof.

A generator that cannot read the kind must fail closed and rewrite nothing. It
must never assume `internal_flext` because a project is registered, present in a
workspace, or written in the same language. Standardizing a fork destroys the
upstream contract the fork exists to track, and the damage is discovered at the
next upstream merge, not at generation time.

## Topology has exactly two values

A repository is `workspace` when it declares `.gitmodules` and composes other
projects, and `standalone` when it does not. There is no third value. `root`,
`member`, `submodule`, `independent`, `parent`, and `child` are prohibited: each
one invents a parallel vocabulary that competes with the declared two and drifts
from it silently.

A project composed by a workspace remains a repository in its own right. It is
described by the same two-value topology and by its own kind, and it follows the
workspace's ledger and shared owners through **declared configuration**, never
through filesystem coupling.

## A cross-project symbolic link is prohibited without exception

A symbolic link tracked by repository A whose target resolves outside A is
prohibited. This holds for every direction and every purpose: a composed project
pointing at its workspace, a workspace pointing at a composed project, either
pointing at a tool cache, a home directory, or a content-addressed store.

The prohibition is absolute because such a link is three defects at once. It is
a second owner of a fact that configuration already declares, so the two drift.
It makes the repository unusable anywhere but one machine's exact layout, so a
clean clone, a worktree, or CI resolves it to nothing or to the wrong target. And
it is invisible to review, because the link reads as a directory.

Shared state is reached by rendering the route into the consuming repository's
own generated configuration — an endpoint, a database name, a declared identity
— which every checkout resolves identically. When a generator currently produces
such a link, the generator is the defect: correct it to render the configuration
and regenerate every consumer in the same cutover. Deleting the links while the
generator still creates them is not a fix.

An existing link is never grandfathered, never a compatibility path, and never
justified by the inconvenience of the configuration it replaced.

See also: `generalized ownership` (rule file) — one writable owner per fact;
`generators, not projections` (rule file) — edit the source and regenerate;
`storage` (rule file) — physical placement and checkout independence.
