# PR Sheriff review triage

Use [scripts/pr_triage.py](../scripts/pr_triage.py) for the mechanical loop; the
judgment stays here.

```sh
# inventory: head/base, mergeability, checks_verdict, blocking/pending checks,
# unresolved threads.
# checks_verdict is the field to read: an empty check set reports
# not_determined, never passed, so a PR whose CI has not started yet cannot be
# mistaken for one whose CI succeeded.
python3 skills/tool/pr-sheriff/scripts/pr_triage.py locate <owner/repo> <pr>

# integration-lane queue across repositories; read each repository's declared
# integration branch from its own law — a branch name written here would be
# wrong for the next repository swept
python3 skills/tool/pr-sheriff/scripts/pr_triage.py sweep <owner/repo>... --base <declared-integration-branch>...

# answer one thread with the evidence file, then resolve it
python3 skills/tool/pr-sheriff/scripts/pr_triage.py settle <thread-id> --body-file evidence.md
```

REST inventories are paginated completely. A completed check is blocking when
its conclusion is anything other than `success`, `neutral`, or `skipped`;
therefore cancelled, timed-out, stale, `action_required`, and startup failures
cannot disappear from the inventory. A check whose status is not `COMPLETED`
remains pending. `mergeability` is explicitly `mergeable`, `conflicting`, or
`unknown`; GitHub's pending `null` is never coerced to `false`.

Triage decision rules, each applied per finding before any reply:

1. **Stale finding** — the reported defect no longer reproduces at the PR head.
   Prove non-reproduction at runtime or by parsing the actual artifact
   (`ast.parse` for import claims, the built binary for behavior claims), reply
   with the exact proof, and resolve the thread. Never resolve on assertion
   alone.
2. **Valid finding with a code owner in this repository** — fix at the owner,
   cite the fix commit in the reply, resolve after push.
3. **Valid finding in a generated projection** — never hand-edit the
   projection; fix the generator SSOT upstream, land its PR, then re-pin
   (lockfile) and regenerate. Reply with the upstream PR reference.
4. **By-design external reference** (governance parent files, fleet skill
   paths) — exclude at the repository's lint config with an override scoped to
   the exact glob, never a blanket rule disable, and say so in the reply.
5. **New findings on the push** — re-reviews re-fire after every push; re-run
   `locate` after each push before declaring the batch settled.

Landing traps that have cost lanes hours, encoded so they stay cheap:

- The PR head branch is the only branch of record. A lane that pushes fixes to
  a same-named local branch without verifying `headRefOid` has landed nothing;
  verify the OID after every push.
- A lockfile pins the generator OID. Landing a generator fix upstream moves
  CI only after the consumer's lockfile re-resolves and the projection is
  regenerated; state which of the two is missing when a gate stays red.
- A committed symlink with an absolute target escapes every CI checkout root;
  generators must render physical files, and adopting the regenerated
  projection is the fix.
