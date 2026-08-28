# Validation and landing

## Evidence contract

Every pass claim records repository, exact source state, command, working
directory, exit code, decisive output, and affected scope. Do not print full
environments, secret values, hashes/fingerprints, raw credential records, or
scanner payloads containing secrets.

During tracker suspension, the manual execution ledger owns current state;
authorized Git commits, PRs, reviews, required checks, and CI own validation and
landing evidence. This documentation package is a specification, not the ledger.

## Runtime before broad gates

Exercise the smallest real public behavior before tests that could otherwise
produce a false green:

- discovery: load every source type and reject a malformed/unknown fixture;
- skills: route a matching request and reject a should-not-trigger request;
- commands: render/invoke representative arguments and reject ambiguous input;
- agents/rules: prove delegation and mandatory-rule behavior;
- projection: apply to isolated personal/project destinations and inspect the
  provider's live loader where available;
- temp/storage: use `agentsctl doctor`, `agentsctl check`, and `agentsctl clean`
  against the configured physical checkout and an isolated generated tree;
- credentials: execute from Bash, Zsh, Fish, and a direct subprocess using only
  the current process environment, without revealing values;
- live model: exact `aihub-primary`, material grader, and explicit error paths.

A runtime failure blocks the phase. Unit tests cannot override it.

## Required semantic scenarios

Each skill has realistic happy-path, empty/ambiguous fail-closed, and
should-not-trigger scenarios with task-specific fixtures and material assertions.
Each command has the seven scenario families in the command contract. Agent
evals prove capability/delegation boundaries; rule evals prove enforcement and
contradiction rejection.

The following never prove success:

- non-empty output;
- `task_completed` without a material grader;
- frontmatter keywords copied into a prompt;
- generic fixtures unrelated to the requested operation;
- a non-empty prompt labeled empty;
- skip, neutral, expected billing/auth failure, or timeout;
- a grader duration equal to the executor timeout.

For a 300-second executor, behavior duration remains below it at 240 seconds.
Authentication, HTTP 402/quota, executor, timeout, and grader errors stay red.

## Runtime and development gate order

The only runtime surface is:

```text
agentsctl help
agentsctl doctor
agentsctl check
agentsctl sync
agentsctl evaluate
agentsctl secure
agentsctl clean
agentsctl live
```

Every line accepts no additional token. Each verb validates its full contract
before effects and aborts on its first exception. `agentsctl live` requires
exact `aihub-primary` and a non-empty valid `CLIPROXY_API_KEY` in the current
process environment; it never reads a credential store or selects another
model.

Make remains development support and gate composition. Its required surface is
discovered with `make help` and covers:

```text
make docs
make audit
make check
make static
make shell
make build
make test
make spec
make coverage
make providers
make projection
make ci
make security
make temp
make validate-live
```

Make targets that exercise runtime call only public `agentsctl` verbs. They do
not import or invoke private runtime functions. Do not invent a missing target
or omit a required target. Correct Make/help/docs at the owner when the
documented surface differs. Formatting or generation gates run in check mode
first; a required rewrite is reviewed as an explicit source change.

## Focused acceptance matrix

| Area | Required proof |
|---|---|
| Documentation | One active master v7 package; links resolve; old plan/type instructions absent. |
| Discovery | Recursive source count/mapping; unknown path/tag/type fails; no name registry consulted. |
| Skills | 76 mapped sources; BPE budgets; short descriptions; semantic scenarios; no command syntax. |
| Commands | Seven flat sources; complete provider render; independent size gate; no skill conversion. |
| Agents/rules | Distribution paths and tags agree; universal rules compose once; no model declaration. |
| Projection | Physical copies; ownership-safe cleanup; provider-native syntax; second apply changes nothing. |
| Temp/storage | Exact manifest; physical registered checkout; `/tmp`, overlap, residue, symlink, special-file, and unknown deletion rejection. |
| Credentials | Process environment only; required values fail immediately; no keyring code, 401, or secret output. |
| Security | Deterministic tracked manifest inventory; every applicable scanner exits zero. |
| CI | PRs to `dev` and all governance source paths execute required native stages. |
| Live Waza | Exact `aihub-primary`; all catalog scenarios material; any service/model failure is red. |

## Contradiction search

After each owner cutover, search source, tests, configs, docs, fixtures, evals,
generated outputs, and supported destinations for:

- old paths and renamed slugs;
- command-as-skill and skill-as-command wording;
- `personal`, `generic`, or registry categories that compete with the six groups;
- word-count token enforcement;
- automatic truncation or normalization of forbidden content;
- silent empty target success;
- symlink/cross-repository references;
- ECC/SkillShare synchronization or current external-import instructions;
- fallback, shim, dual-read/write, alternate model, skip, suppression, and old
  `~/.agents` source lookups after cutover.
- exception catches outside cleanup/rollback, aggregate validators, manual exit
  translation, retry loops, undeclared or error-triggered defaults, partial
  publication, and any keyring source or consumer. Canonical calculated defaults
  declared once at their typed owner are valid.

Any active opposite blocks integration.

## Landing contract

When Git execution is authorized:

1. fetch the configured integration branch and record its SHA;
2. if divergent, merge `origin/<integration>` into the work lane with
   `git merge --no-ff origin/<integration>`;
3. resolve conflicts by preserving every valid concurrent owner change;
4. rerun representative runtime and all required gates;
5. commit scoped files and push normally, never force-push;
6. open/update a PR against the configured integration branch;
7. resolve every conversation and required check and obtain independent approval;
8. merge through a merge commit, not squash or rebase;
9. validate runtime and complete gates on the exact integration merge SHA;
10. remove only clean, reachable increment branches through safe deletion.

A phase is `DONE` only after its approved PR is merged, post-merge runtime is
green, and its canonical Bead is closed with evidence. While tracker runtime is
suspended, record state in the manual execution ledger and stop at
`LANDED_VERIFIED`; the ledger cannot substitute for tracker closure.
