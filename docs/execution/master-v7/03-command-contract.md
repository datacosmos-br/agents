# Command contract

This contract governs provider-authored commands under `commands/`. It does not
expand the deterministic runtime CLI: `agentsctl` remains limited to its eight
optionless single verbs and never accepts provider-command arguments.

## Canonical layout

```text
commands/
├── add-language-rules.md
├── database-migration.md
├── feature-development.md
├── ghi-list.md
├── pr-list.md
├── ralph-loop.md
└── security-triage.md
```

The target has seven flat commands: the existing `security-triage` command and
six artifacts converted from misclassified skills. Canonical command names stay
flat and preserve their public slugs. Category namespaces are not introduced in
this cutover.

`simplify` remains an inline skill. The deleted `commands/simplify.md` is not
restored, and broken personal projections of that removed command must be
removed by ownership-aware projection cleanup.

## Source schema

Every command has:

```yaml
---
name: feature-development
description: Implement one approved feature through project owners and gates.
argument-hint: "<feature or approved specification>"
metadata:
  aihub.tags: '["intent:implementation","risk:write","route:project"]'
---
```

Required invariants:

- `name` equals the filename slug.
- `description` is one short picker sentence, not a command body.
- `argument-hint` is present when arguments affect target or behavior.
- Tags include exactly one `route:agent|project`, at least one
  `intent:planning|implementation|inspection|verification|landing|governance`,
  and exactly one primary `risk:read|write|external`.
- The body defines input validation, owner discovery, execution steps, failure
  propagation, expected output/evidence, and should-not-run conditions.
- A mutating or external command cannot be model-auto-invoked.
- Missing, invalid, or genuinely ambiguous input fails before side effects.

## Separate size policy

The command body may exceed 5,000 BPE tokens when the workflow requires it. It
is never checked against skill router or procedure budgets. Validation counts
the fully rendered provider command with a model-compatible BPE tokenizer and
checks the provider's documented context limit. If complete rendering cannot
fit, the adapter fails with command, provider, measured tokens, and limit.

Never truncate, summarize automatically, split into hidden commands, or compile
a long command into a fake skill to force a pass.

## Provider adapter matrix

| Provider | Native command destination | Rendering contract |
|---|---|---|
| Claude | `.claude/commands/<slug>.md` | Markdown command; retain explicit invocation and manual-only behavior for mutations. |
| Gemini | `.gemini/commands/<slug>.toml` | TOML with required `prompt`; map canonical arguments to `{{args}}`; reject unsafe shell/file interpolation not present in the source contract. |
| OpenCode | configured global/project command root | Markdown template; reject source or generated `model`, `agent`, `subtask`, shell injection, and built-in override. |
| Cursor | project `.cursor/commands/<slug>.md` | Markdown command using only fields supported by the installed client; personal projection is unsupported unless current official behavior proves it. |
| GitHub Copilot CLI | officially supported command root for the installed version | Render only documented fields; command remains lower-level provider output, not a canonical skill. |
| Codex | none | Return explicit `UNSUPPORTED`; never project canonical commands as skills or legacy custom prompts. |
| Antigravity | none until canary | Keep disabled until the installed official client proves destination, reload, invocation, and size behavior. |

Primary provider references:

- [Claude commands and skills](https://code.claude.com/docs/en/slash-commands)
- [Gemini CLI custom commands](https://geminicli.com/docs/cli/custom-commands/)
- [OpenCode commands](https://opencode.ai/docs/commands/)
- [Cursor commands](https://docs.cursor.com/en/agent/chat/commands)
- [GitHub Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [Codex custom-prompt removal confirmation](https://github.com/openai/codex/issues/15941)

Installed-version behavior and official current documentation both gate an
adapter. A foreign command already present in a destination is preserved and
reported unless its ownership manifest proves this repository created it.

## Collision and safety policy

- A canonical command slug must not collide with a canonical skill, provider
  built-in, installed plugin command, or foreign destination command.
- Apply fails before writes when a collision exists.
- Rendered provider interpolation is typed. User text cannot create an
  undeclared shell command, file read, tool permission, model override, or
  subagent delegation.
- A command that invokes external tools verifies availability and auth before
  mutation; missing auth remains red.
- A command reports causal runtime failure. It never returns success because it
  produced non-empty text or because a required step did not run.

## Command evaluation

Each command has at least:

1. realistic invocation with material output or artifact assertion;
2. empty or ambiguous invocation that fails before effects;
3. should-not-run scenario;
4. argument-rendering tests for every supported provider;
5. explicit unsupported-provider test;
6. collision, injection, and oversize tests;
7. two-run projection fixed point.

Command evals are not counted as skill scenarios and do not affect skill token
budgets or activation precision metrics.
