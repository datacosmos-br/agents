# Authority and scope

## Outcome

Reorganize the current `.agents` artifact inventory by explicit semantic
contracts, validate it through Waza and provider adapters, and land it on the
configured integration branch without importing new external content or using
suspended runtimes.

## Included

- Documentation, decisions, discovery, validation, and migration of the current
  skills, commands, agents, rules, and their governance code. Repository hooks
  are removed because agent-domain behavior has one CLI facade.
- Recursive path-derived discovery, local semantic tags, deterministic physical
  projections, provider adapters, Waza scenarios, and fixed-point checks.
- The six accepted review corrections: CI path coverage, owned process-group
  termination, BPE token counting, forbidden-update preservation, MCP drift
  failure, and unknown projection-target rejection.
- Existing storage, direct-environment credential, CI, security, and model-owner
  work needed for a complete repository landing.
- Complete removal of keyring code, integration, documentation, entry points,
  loaders, and tests. Existing external keyring values are outside scope and
  remain uninspected and untouched.

## Excluded

- Any skill, command, agent, or rule import from ECC, SkillShare, FLEXT,
  marketplaces, plugins, other repositories, or provider examples.
- Any synchronization or updater that keeps a foreign source as a competing
  runtime authority.
- Unrequested changes, branches, PRs, or runtime calls in another repository.
  `agentsctl sync` is reusable project infrastructure and applies only to the
  current process home and physical Git project from which the operator invokes
  it.
- Beads, Dolt, Gas City, Gas Town, and alternate tracker runtimes while they are
  suspended. Create no substitute tracker or ledger; preserve evidence only in
  separately authorized Git/PR/CI surfaces.
- Promotion beyond the configured integration branch, package publication,
  release, tag, or unrelated credential changes.
- Relocation of any physical owner beyond the workspace contract already
  declared by the operator; `~/agents` is the current canonical root.

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
- Staging and backups remain on the destination filesystem. Projection has one
  physical copy implementation and never retries through another strategy.
- Never remove a live process, valid lock, dirty Git tree, database, symlink, or
  unknown content.
- No workflow retries or substitutes a failed copy strategy. If the one
  selected operation cannot satisfy the destination contract, it raises before
  publication completes.
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

## Invocation stop conditions

Stop the current invocation with exact evidence when:

- a command would invoke a suspended runtime;
- an artifact cannot be classified from its actual behavior;
- two current owners claim the same fact or destination;
- a provider lacks the required native capability;
- a generated destination contains unattributable or foreign content;
- a secret, model, scanner, runtime, test, review, or required check fails;
- safe absorption of concurrent work cannot be proven;
- an implementation requires a public interface not approved in this package.

The first defect raises immediately with its raw traceback and causal chain.
Do not translate a stop condition into a finding, warning, skip, empty result,
manual exit code, retry, fallback, fake skill, alternate model, suppression,
weakened gate, compatibility path, or partial success claim.

The phase remains active. Correct each actionable owner and rerun the invalidated
runtime, gate, review, publication, or integration step. Request operator help
only after no authorized technical correction remains and the condition is
external or requires new authority; never switch work by reporting this state.
