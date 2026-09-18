# Legacy pack formulas

These require the legacy pack. They extend the built-in `mol-polecat-base`.

**mol-polecat-work** — Feature-branch variant. Creates a worktree and feature branch,
implements, then pushes and reassigns to the refinery for merge review. Production
default for multi-agent setups.

```text
gc sling <agent> <bead-id> --on mol-polecat-work
```

The polecat cuts its branch from `origin/<base_branch>` and stamps `metadata.target` for
the refinery, so `base_branch` decides where the work lands. `gc sling` resolves it in
this order, first match wins:

1. `metadata.target` on the work bead, or on the nearest parent convoy that carries one
   — the per-bead override.
2. `default_branch` recorded for the bead's rig in `city.toml`.
3. `default_branch` recorded for the agent's rig in `city.toml`.
4. A live probe of the rig repo's `origin/HEAD`.

Tiers 2 and 3 are the knob to reach for when a repo's mainline is not what `origin/HEAD`
advertises. A repo whose `origin/HEAD` still points at a mirror-only `main` while work
belongs on an integration branch sets it once, per rig:

```toml
[[rigs]]
name = "myrig"
default_branch = "develop"
```

Without that, resolution falls through to the tier-4 probe and every polecat branch is
cut from the mirror. `gc rig add` captures `default_branch` from the repo at add time,
so a rig registered before its mainline moved keeps the stale value until you update it
— check `gc rig list --json` rather than inferring the answer from
`git symbolic-ref refs/remotes/origin/HEAD`, which only ever reports tier 4.

**mol-idea-to-plan** — Planning workflow for a coordinator session. Turns a rough idea
into a PRD, reviewed design doc, and beads DAG using Gas City's existing primitives:
repo-local artifact files, review task beads, `gc sling`, and mail. Best run from a crew
worker in the target rig.

```text
gc sling <coordinator-agent> -f mol-idea-to-plan --var problem="..." --var review_target=<rig>/polecat
```

**mol-review-leg** — Helper formula used by `mol-idea-to-plan` review tasks. Persists
the full report to bead notes, mails the coordinator, closes the bead, and drains the
session. Usually not slung by hand.

## Legacy pack formulas (patrol loops)

Patrol formulas are auto-poured by agent startup prompts — you typically don't sling
these manually:

- **mol-refinery-patrol** — Refinery merge loop (check for work, merge one branch,
  repeat)
- **mol-witness-patrol** — Rig work-health monitor (orphan recovery, stuck polecats,
  help mail)
- **mol-deacon-patrol** — Controller sidekick (work-layer health, system diagnostics)
- **mol-shutdown-dance** — Due process for stuck agents (interrogate → execute →
  epitaph)

`mol-digest-generate` (the periodic activity digest mailed to the mayor) is **not** a
startup patrol pour: it is driven by an `order` on a schedule (the `digest-generate`
order — a 24h cooldown trigger). Run or inspect it through its order
(`gc order run digest-generate`, `gc order show digest-generate`), not as a manual sling
or a patrol pour.
