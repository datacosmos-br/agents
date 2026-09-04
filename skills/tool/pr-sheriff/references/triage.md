# PR Sheriff review triage

Read repository-local configuration and optional AI Hub association metadata,
then use the existing Git and GitHub configuration directly:

```sh
git remote get-url origin
git ls-remote origin HEAD
```

Never mutate `~/.ssh/config`, introduce a host alias, execute Python directly,
or invoke a helper script through its shebang. Do not rewrite a functioning
remote to satisfy a separate access policy.

Collect the complete PR inventory with `gh pr list`, then query each PR with
`gh pr view --json` for head/base OIDs, draft/state, mergeability, merge state,
reviews and check rollup. Query unresolved review threads through paginated
`gh api graphql`; an empty check set is not determined, never passed. A check
not completed stays pending, and every completed conclusion other than the
repository's accepted success conclusions remains blocking.

Immediately before an authorized merge, repeat the PR query and require the
declared integration base, the authorized head OID, open non-draft state,
mergeable/clean state, passed native CI owner, required approval and zero
unresolved threads. Bind the merge to that same OID:

```sh
gh pr merge <pr> --merge --match-head-commit <authorized-head-oid>
```

Triage each finding:

1. For a stale finding, prove non-reproduction against the current head before
   replying and resolving.
2. For a valid repository finding, correct its owner, push, re-query the head
   OID and rerun invalidated gates.
3. For generated output, correct and land the generator, update its pin and
   regenerate the consumer.
4. For an intentional external reference, use the narrow repository-owned
   configuration override; never disable a rule globally.
5. After every push, query all checks, reviews and threads again.

The PR head is the branch of record. A local same-named branch is not evidence.
Never land from a stale OID, treat GitHub's pending mergeability as false, or
claim completion before the integration SHA and post-merge runtime proof.
