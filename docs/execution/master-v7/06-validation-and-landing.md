# Validation and landing

## Evidence contract

Every pass claim records repository, exact source state, command, working
directory, exit code, decisive output, and affected scope. Do not print full
environments, secret values, hashes/fingerprints, raw credential records, or
scanner payloads containing secrets.

During tracker suspension, authorized Git commits, PRs, reviews, required checks,
and CI are the only durable implementation evidence. This documentation package
is a specification, not a manual ledger.

## Runtime before broad gates

Exercise the smallest real public behavior before tests that could otherwise
produce a false green:

- discovery: load every source type and reject a malformed/unknown fixture;
- skills: route a matching request and reject a should-not-trigger request;
- commands: render/invoke representative arguments and reject ambiguous input;
- agents/rules: prove delegation and mandatory-rule behavior;
- projection: apply to isolated personal/project destinations and inspect the
  provider's live loader where available;
- temp: run a real child tree and interrupt it;
- credentials: login/interative shells, direct auto-exec, Mise, GitHub API, and
  proxy without revealing values;
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

## Native gate order

Discover the actual Make surface with `make help`, then run the owner-approved
equivalents of:

```text
make check
make static
make shell
make build
make test
make spec
make coverage
make ci
make security
make sync
make temp
make validate-live
```

Do not invent a missing target or mark it skipped. Correct Make/help/docs at the
owner when the documented surface differs. Formatting or generation gates run
in check mode first; a required rewrite is reviewed as an explicit source change.

## Focused acceptance matrix

| Area | Required proof |
|---|---|
| Documentation | One active master v7 package; links resolve; old plan/type instructions absent. |
| Discovery | Recursive source count/mapping; unknown path/tag/type fails; no name registry consulted. |
| Skills | 76 mapped sources; BPE budgets; short descriptions; semantic scenarios; no command syntax. |
| Commands | Seven flat sources; complete provider render; independent size gate; no skill conversion. |
| Agents/rules | Distribution paths and tags agree; universal rules compose once; no model declaration. |
| Projection | Physical copies; ownership-safe cleanup; provider-native syntax; second apply changes nothing. |
| Temp/storage | Concurrent isolation; owned group stops; live/dirty/database/symlink/unknown fixtures survive. |
| Credentials | Two physical sources; aliases resolve in memory; no 401 and no secret output. |
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
suspended, stop at `LANDED_VERIFIED` and do not create a substitute closure
record.
