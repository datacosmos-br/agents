# Authority and scope

## Outcome

Reorganize the current `.agents` artifact inventory by explicit semantic
contracts, validate it through Waza and provider adapters, and land it on the
configured integration branch without importing new external content or using
suspended runtimes.

## Included

- Documentation, decisions, discovery, validation, and migration of the current
  skills, commands, agents, rules, hooks, and their governance code.
- Recursive path-derived discovery, local semantic tags, deterministic physical
  projections, provider adapters, Waza scenarios, and fixed-point checks.
- The six accepted review corrections: CI path coverage, owned process-group
  termination, BPE token counting, forbidden-update preservation, MCP drift
  failure, and unknown projection-target rejection.
- Existing storage, credential, CI, security, and model-owner work needed for a
  complete repository landing.
- Final owner relocation from `~/.agents` to `~/agents` only after all active
  processes have left the old checkout and every earlier phase is integrated.

## Excluded

- Any skill, command, agent, or rule import from ECC, SkillShare, FLEXT,
  marketplaces, plugins, other repositories, or provider examples.
- Any synchronization or updater that keeps a foreign source as a competing
  runtime authority.
- Changes, projections, branches, PRs, or runtime calls in another repository.
- Beads, Dolt, Gas City, Gas Town, and alternate tracker runtimes while they are
  suspended. Use the repository manual ledger for execution state.
- Promotion beyond the configured integration branch, package publication,
  release, tag, or unrelated credential changes.

## Authority and precedence

Newest explicit operator instructions supersede older plans, tracker text,
ADRs, skills, and documentation. The master v7 package supersedes master v6 and
all conversation-only plan variants for this increment. If a new instruction
conflicts with this package, update the canonical owner and remove the opposing
active instruction in the same change; do not retain both as alternatives.

## Filesystem and execution law

- Work only in the existing checkout while orchestration is suspended.
- Do not create a clone, worktree, alternate checkout, symlink, or
  cross-repository reference.
- `/tmp` is limited to small bounded OS primitives. It is never a workspace,
  clone staging area, backup destination, report store, database, reusable
  cache, or build root.
- Staging and backups remain on the destination filesystem. Linux copy
  operations use `cp --archive --reflink=auto` where supported.
- Never remove a live process, valid lock, dirty Git tree, database, symlink, or
  unknown content.
- Do not rebase, force-push, destructively reset, globally stash, or edit the
  integration branch directly.

## Tracker suspension

The automatically injected Beads help text is not runtime authorization. Active
repository law explicitly suspends Beads, Dolt, and Gas City. Do not run `bd`,
`dolt`, `gt`, or `gc`, select a port, start a server, or create an embedded or
alternate database. Do not materialize a task list to imitate the tracker.

When runtime is explicitly restored, use only its then-current canonical help
and repository owner. Historical endpoint, flag, prefix, or database knowledge
is not reusable authority.

## Stop conditions

Stop the affected phase and report exact evidence when:

- a command would invoke a suspended runtime;
- an artifact cannot be classified from its actual behavior;
- two current owners claim the same fact or destination;
- a provider lacks the required native capability;
- a generated destination contains unattributable or foreign content;
- a secret, model, scanner, runtime, test, review, or required check fails;
- safe absorption of concurrent work cannot be proven;
- an implementation requires a public interface not approved in this package.

Do not translate a stop condition into a fallback, fake skill, alternate model,
suppression, weakened gate, or partial success claim.
