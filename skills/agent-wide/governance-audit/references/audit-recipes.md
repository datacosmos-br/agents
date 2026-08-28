# Governance audit recipes

These recipes classify supplied governance evidence without mutating its owner.

## Runtime preflight

Determine the declared tracker, documentation authority, projection owner, and
runtime state before inspection. When the tracker is suspended or unavailable,
use only supplied static snapshots and repository files. Do not invoke a tracker,
select an endpoint, or substitute another database.

After explicit runtime restoration, read the then-current canonical help before
selecting any read-only command. Historical flags, endpoints, and command examples
are not reusable authority. A missing inspection surface is the first blocker.

## Tracker-state checks

- status conflicts: work marked in progress while an open dependency blocks it;
- stale blocks: blocked work whose declared blocker is no longer open;
- ownerless or workerless in-progress work;
- open epics without a material description;
- claim concentration and priority inflation;
- overlapping epics and drain candidates.

Timestamps alone do not prove staleness. Inspect content, declared dependencies,
live ownership, and current runtime evidence.

## Content and projection checks

- resolve every cited file and tracker identifier through its canonical owner;
- identify closed ancestors still presented as live context;
- compare canonical source bytes with declared physical projections;
- treat dual writable paths or source/projection divergence as blocking;
- preserve projections during audit and recommend correction at the source owner.

## Severity and report

- **P0**: dual mutating orchestrators, ownerless in-flight work, or two writable truths;
- **P1**: stale blocks, missing epic contract, claim concentration, zombie work, or canonical-link rot;
- **P2**: priority inflation, note archaeology, dead references, or non-authoritative prose drift.

Report: check | finding | evidence | owner-correct action | severity. Evidence
must identify its source or read-only command and decisive result. Stop at the
first causal inspection defect; do not aggregate later checks after it fails.
