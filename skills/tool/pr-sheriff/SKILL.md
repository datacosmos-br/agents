---
name: pr-sheriff
description: 'pull requests, review triage, github workflow'
allowed-tools: Bash(gh pr *), Bash(git *)
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:pr-sheriff","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:github","updates:manual","usage:on-demand"]'
  author: .agents
  version: 3.1.0
---

# PR Sheriff

Activate only for explicit pull-request triage or landing in one repository selected by active configuration. Never infer a repository or scan an organization. Follow the complete [router procedure](references/router-procedure.md) and preserve its owners, evidence contracts, failure propagation, and required output standard.

## Review-comment triage tooling

Use [scripts/pr_triage.py](scripts/pr_triage.py) for the mechanical loop; the
judgment stays here.

```sh
# inventory: head/base, mergeable, failing/pending checks, unresolved threads
python3 skills/tool/pr-sheriff/scripts/pr_triage.py locate <owner/repo> <pr>

# integration-lane queue across repositories
python3 skills/tool/pr-sheriff/scripts/pr_triage.py sweep <owner/repo>... --base dev,develop,0.12.0-dev

# answer one thread with the evidence file, then resolve it
python3 skills/tool/pr-sheriff/scripts/pr_triage.py settle <thread-id> --body-file evidence.md
```

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
