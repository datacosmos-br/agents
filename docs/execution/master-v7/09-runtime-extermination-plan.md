# Runtime strict-extermination plan

## Exclusive objective

Establish the documentation and central policy authority, then refactor the
complete governance runtime. This plan does not modify `skills/**` or any
catalog-skill Waza suite under `evals/<skill-slug>/**`.

The implementation is fail-loud by construction: the first exception terminates
execution with its raw traceback and chained cause. Errors never become findings,
warnings, skips, neutral results, empty collections, hand-selected exit codes,
retries, fallbacks, alternate providers, undeclared, competing, or
error-triggered defaults, compatibility, or partial execution. Canonical
calculated defaults resolve once at their typed owner and are omitted from
consumers. Only cleanup and rollback may catch; secondary failures are attached
to and re-raise the original cause.

## Fixed execution order

1. Commit these two standalone plans before any other mutation.
2. Reconcile every active document with the strict contract and remove every
   contradictory instruction.
3. Create one central rule for each policy.
4. Exterminate keyring and refactor environment, storage/temp, security,
   atomic I/O, subprocess, cleanup, and rollback without touching the skills
   lane.
5. After the skill-lane handoff, enforce policy tags in the catalog, regenerate
   `skills.lock.json` once, and prove a second generation is unchanged.
6. Complete the optionless `agentsctl`, projection v5, Waza, Make, CI, runtime,
   integration, review, and landing cycle.

## Central policies

The mandatory vocabulary is `policy:strict-execution`, composed from:

- `policy:fail-loud`;
- `policy:no-fallback`;
- `policy:preflight-before-effects`;
- `policy:required-environment`;
- `policy:atomic-effects`;
- `policy:causal-subprocess`;
- `policy:no-keyring`;
- `policy:zero-residue`.

Universal and project rule composition applies this baseline to every project,
whether or not a skill is activated. No skill, agent, provider, project, config,
or caller can weaken or disable it.

## Runtime and CLI outcome

Delete the complete keyring contract and all of its code, entry points,
configuration, profiles, aliases, auto-load/auto-exec paths, events, state,
shell hooks, rules, tests, and consumers. Existing GNOME Keyring values are not
inspected or administered. Live Waza accepts only a present, non-empty
`CLIPROXY_API_KEY` and validates it before any effect.

`agentsctl` becomes the only CLI. It accepts exactly one optionless verb:
`help`, `doctor`, `check`, `sync`, `evaluate`, `secure`, `clean`, or `live`.
Each verb runs its complete workflow over the canonical inventory. The CLI and
orchestrators contain no catches. Make owns only development support and gate
composition; all agent-domain behavior belongs to these verbs.

`sync` is the complete selected-projection workflow. It derives one physical Git
root from cwd and the current process home. Invocation selects personal
surfaces; the strict project-owned selection additionally authorizes project
surfaces. It preflights every selected surface and publishes directory and
instruction artifacts atomically. It has no personal mode, no hook subcommand,
and no lifecycle-hook surface.

## Enforcement and landing

An AST gate rejects catches outside cleanup/rollback, `check=False`, findings,
warnings, skips, retries, fallbacks, undeclared or error-triggered environment
defaults, alternate providers/models/credentials, neutral error returns, manual
exit translation, and compatibility readers. Semantic searches prove zero keyring, old CLI,
option, argparse, JSON-output, and old-contract residue.

Every mutating workflow validates all sources, inputs, variables, destinations,
ownership, collisions, and candidates before its first effect. Publication is
atomic; rollback failure is attached to the original publication failure.

When Git is authorized, publish a WIP commit after every coherent unit. While
tracking is suspended, create no substitute tracker or ledger. Integrate `origin/dev` only with
`git merge --no-ff`, revalidate the integrated SHA, and land by independently
approved merge commit. Never rebase, squash, force-push, destructively reset, or
stash. Beads, Dolt, Gas City, and Gas Town remain suspended. The maximum state is
`LANDED_VERIFIED`, never `DONE`.
