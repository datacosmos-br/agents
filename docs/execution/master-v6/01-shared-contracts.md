# Shared contracts

## Credential contract

Exactly two physical records own GitHub/proxy credentials in the relevant
profile:

```text
GITHUB_TOKEN
PROXY_INTERNAL_API_KEY
```

Exports are aliases of those records:

```text
GH_TOKEN                 -> GITHUB_TOKEN
GITHUB_PAT               -> GITHUB_TOKEN
GITHUB_API_TOKEN         -> GITHUB_TOKEN
MISE_GITHUB_TOKEN        -> GITHUB_TOKEN
CLIPROXY_API_KEY         -> PROXY_INTERNAL_API_KEY
COPILOT_PROVIDER_API_KEY -> PROXY_INTERNAL_API_KEY
```

Mise checks `MISE_GITHUB_TOKEN`, `GITHUB_API_TOKEN`, then `GITHUB_TOKEN`.
Bootstrap must clear every declared canonical and alias name before injecting
the canonical value. See the
[Mise GitHub token reference](https://mise.jdx.dev/dev-tools/github-tokens.html).

`env-keyring remove --profile P --name N --yes`:

- accepts only a declared canonical or alias name;
- canonical input removes only the canonical physical record;
- alias input removes only a legacy physical record named by that alias;
- never follows an alias to delete its canonical source;
- emits no value, hash, fingerprint, or fragment;
- refuses an undeclared name or missing `--yes`.

Before deleting duplicates, compare values internally. A mismatch preserves all
records and fails. The two-record limit applies only to this credential domain;
unrelated keyring profiles and secrets remain untouched.

## Waza contract

`config/model-pipeline.json` is the only model-pipeline owner. It contains only the
stable alias `ai-hub-primary`. `agentsctl model-pipeline` exposes exactly:

- `check` — validate every generated repository surface without writing;
- `apply` — materialize the alias and reach a fixed point;
- `resolve` — print only the stable alias;
- `probe` — require the injected provider to publish that exact alias.

Concrete provider models, model families, tiers, variants, effort levels, and
caller overrides are forbidden in this repository. The upstream model pipeline
owns their selection.

`apply` changes only generated model projections and unsupported model metadata;
it must produce no diff on the second run.

Every active skill has three semantic scenarios:

- realistic happy path with a compatible fixture;
- genuinely empty/ambiguous edge case that fails closed;
- should-not-trigger case with a negative expectation.

Success requires a specific result, artifact, or behavior. These are not proof:

- `len(output) > 0`;
- `task_completed` without a material grader;
- frontmatter keywords copied into a prompt;
- a generic `sample.py` unrelated to the task;
- a non-empty prompt named “Empty Input”;
- a duration grader equal to the executor timeout.

For a 300-second executor timeout, `max_duration_ms` is 240000. Authentication,
quota, timeout, executor, and grader errors remain red. Claude HTTP 402 maps to
`MODEL_UNAVAILABLE`; it never triggers a model switch or baseline publication.

## Migration contract

`database-migration` must reject work until a public contract change is
approved. An accepted migration has one final schema, transforms atomically and
idempotently, rewires every consumer, rejects the old format, and removes old
code, fixtures, examples, and docs.

Fallbacks, shims, dual-read, dual-write, deprecation-only coexistence, and
postponed cleanup are defects. Environment aliases in the credential contract
are multiple consumption names for one secret, not schema compatibility.

## Skill distribution contract

| Class | Destination | Required behavior |
|---|---|---|
| Personal | Agent homes | Workflows and non-technological personal capabilities only. |
| Generic | Project `.agents` | Repository-independent engineering capability only. |
| Technology | Matching projects | Detect markers/dependencies before physical installation. |
| FLEXT | Proven FLEXT projects | Source semantics from the FLEXT owner; generator may live in FLEXT Infra. |
| Personal governance | Agent homes | `gascity-workspace-lifecycle` and `gascity-change-lifecycle`; never project to projects. |

Project content must not teach AI Hub, `.agents`, tracker, or orchestrator development
workflows. It must not contain a local absolute path, symlink, or cross-repo
reference. Projection uses physical copies and reflinks when available.

Approved projection interfaces:

```text
agentsctl discover-projects --root <repo>...
agentsctl project --scope projects --root <repo>... --check|--apply
```

Roots are explicit and repeatable. Invalid roots and unmatched targets fail.
The second apply must be a fixed point.

## Storage contract

`AGENTS_STORAGE_CONFIG` names the exact storage manifest. No `$HOME` discovery
or alternate implicit manifest is allowed.

- Scratch is exclusive per invocation.
- `TMPDIR`, `GOTMPDIR`, and `GOCACHE` are exclusive for test/build runs.
- `GOMODCACHE` is shared.
- Reusable cache uses XDG cache; state and evidence use XDG state.
- Warn at 1 GiB and fail at 5 GiB per managed run.
- GC is dry-run by default and fail-closed.
- Cleanup never removes a live process, valid lock, dirty Git tree, database,
  symlink, or unknown content.

## Security contract

- Inventory tracked manifests and lockfiles deterministically. Do not rely on a
  monolithic best-effort scan.
- Run Snyk per manifest/project. Exit 1, 2, and 3 fail. See the
  [Snyk CLI reference](https://docs.snyk.io/snyk-cli/commands/test).
- Run Semgrep, Gitleaks, ecosystem audits, native scanners, and Actions checks
  applicable to each repository.
- No suppression, ignored severity, omitted project, accepted risk, or
  `|| true` is allowed.
- Pin third-party Actions to full commit SHAs. GitHub documents this as the
  immutable reference method in its
  [secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
- Dependabot cooldown applies to version updates, not security updates. See the
  [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference).
- uv cooldowns use a duration such as `7 days`; resolution materializes the
  effective timestamp in the lockfile. See the
  [uv resolution reference](https://docs.astral.sh/uv/concepts/resolution/).

## Landing contract

Each lane must fetch its integration branch. When the branch diverges, merge
the integration base into the work branch:

```bash
git merge --no-ff origin/<integration>
```

Then run runtime, tests, static checks, build, and security before normal push.
The PR targets the configured integration branch and merges by merge commit.
GitHub must require a PR, one approval, successful checks, and resolved
conversations. Force-push and deletion stay disabled. Linear history stays
disabled because it rejects merge commits. See
[GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
and [merge methods](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request).
