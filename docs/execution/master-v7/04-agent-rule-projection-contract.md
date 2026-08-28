# Agent, rule, and projection contracts

## Agent distribution

Agents use distribution directories only:

```text
agents/
├── agent-wide/
└── project-wide/
```

- `agent-wide` is projected to every authorized personal agent environment and
  never into a project.
- `project-wide` is available to project projections, subject to provider
  capability and any declared detector tags.

The approved always-personal set is:

- `chief-of-staff`
- `loop-operator`
- `docs-lookup`
- `homelab-architect`
- `seo-specialist`
- `harness-optimizer`
- `marketing-strategist` (rename of `marketing-agent`)
- `prompt-engineer`

The approved removals are exactly:

- `blueprint-mode`, `code-architect`, `code-explorer`,
  `conversation-analyzer`, `executor`, `gan-evaluator`, `gan-generator`,
  `gan-planner`, `janitor`, `playwright-tester`,
  `principal-software-engineer`, `software-engineer`, `tdd-green`, `tdd-guide`,
  `tdd-red`, and `tdd-refactor`.

The approved renames are exactly:

- `a11y-architect` → `accessibility-architect`
- `architect` → `system-architect`
- `build-error-resolver` → `typescript-build-resolver`
- `database-reviewer` → `postgresql-reviewer`
- `debugger` → `root-cause-debugger`
- `devops-expert` → `devops-engineer`
- `doc-updater` → `documentation-maintainer`
- `marketing-agent` → `marketing-strategist`
- `planner` → `implementation-planner`
- `platform-sre-kubernetes` → `kubernetes-sre`
- `refactor-cleaner` → `dead-code-cleaner`

`harmonyos-app-resolver` is split into `harmonyos-build-resolver` and
`harmonyos-reviewer` by moving only its existing build/implementation and review
responsibilities. This split is separate from the eleven simple renames.

Every other current agent undergoes content-level capability comparison before
movement. Generic provider/built-in duplicates, the GAN trio, and fragmented
TDD phase agents are removed after unique behavior is absorbed into the
appropriate surviving owner. Build resolver and reviewer variants survive only
when they add stack-specific behavior that a tagged project-wide agent cannot
express without becoming a god prompt.

Agent tags describe orthogonal facets rather than folders:

- `mode:plan|execute|review|debug|operate`
- `technology:*`, `framework:*`, `tool:*`, `domain:*`
- `capability:*`
- `activation:always|detected|opt-in`
- `detect:*` when conditional

No target count is permitted. Discovery must fail on an undecided duplicate or
ambiguous responsibility rather than force it into a balanced category.

## Universal rule composition

Universal engineering behavior is injected as rules, not repeated inside every
skill or agent. The composed baseline includes the active project law plus the
contracts represented by:

- search-first;
- YAGNI, SSOT, SOLID, DRY, and simplify;
- fail-fast and anti-hardcode;
- anti-phase-skip and verification-loop;
- security, storage, and landing law.

Each provider adapter renders the same semantics through its supported
instruction surface. Provider-specific wording may adapt invocation, tool, and
path mechanics, but it cannot weaken or expand the canonical rule. Repeated
agent-local policy blocks are removed after rule composition proves equivalence.

Rules are always active or path scoped. They are not selectable skills and do
not carry skill descriptions or Waza activation scenarios. Rule validation uses
contradiction, coverage, provider-rendering, and runtime behavior tests.

The canonical execution order is owned once by
`rules/architecture/engineering-core.md`. Detailed skills remain selectable
procedures; agents and provider adapters consume the concise rule and do not
paste those procedures into every profile.

## Verified provider instruction surfaces

The word “rule” is not assumed to name the same artifact across providers. The
adapter is allowed only on the provider's documented instruction surface:

| Provider | Personal instructions | Project instructions | Item-scoped rule files |
|---|---|---|---|
| Claude Code | `~/.claude/rules/**/*.md` | `.claude/rules/**/*.md` | Yes; `paths` frontmatter |
| Cursor | Settings-owned user rules | `.cursor/rules/*.mdc` | Project only; `globs` and `alwaysApply` |
| Copilot CLI | `~/.copilot/instructions/**/*.instructions.md` | `.github/instructions/**/*.instructions.md` | Yes; `applyTo` frontmatter |
| Antigravity | `~/.gemini/GEMINI.md` | `.agents/rules/*.md` | Project only; each rule is limited to 12,000 characters |
| Gemini CLI | `~/.gemini/GEMINI.md` | hierarchical `GEMINI.md` | No item-scoped rule directory |
| OpenCode | `~/.config/opencode/AGENTS.md` | hierarchical `AGENTS.md` | No item-scoped rule directory |
| Codex | `~/.codex/AGENTS.md` | hierarchical `AGENTS.md` | No Markdown rule directory |

Codex `.codex/rules/*.rules` is an execution-policy language written in
Starlark. It is not an engineering-instruction surface and must never receive
canonical Markdown rules. Aggregated `AGENTS.md` or `GEMINI.md` projection is a
separate whole-file compiler with whole-file ownership; until that compiler is
implemented and proves foreign-content safety, the combination is
`UNSUPPORTED`, not approximated with includes, managed fragments, or another
artifact type.

Canonical references:

- [OpenAI Codex `AGENTS.md`](https://developers.openai.com/codex/guides/agents-md)
  and [execution-policy rules](https://developers.openai.com/codex/agent-configuration/rules);
- [Claude Code memory and rules](https://code.claude.com/docs/en/memory);
- [Cursor rules](https://docs.cursor.com/context/rules);
- [GitHub Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions);
- [Gemini CLI context](https://geminicli.com/docs/cli/gemini-md/) and
  [subagents](https://geminicli.com/docs/core/subagents/);
- [OpenCode instructions](https://opencode.ai/v2/docs/instructions);
- [Antigravity rules and workflows](https://antigravity.google/docs/rules-workflows).

## Projection matrix

| Source | Personal agent homes | Project destinations |
|---|---|---|
| `skills/agent-wide` | Always | Never |
| `skills/project-wide` | Never as personal-only content | Always |
| `skills/technology` | Never by default | Only when marker/dependency detector passes |
| `skills/framework` | Never by default | Only when dependency/marker detector passes |
| `skills/tool` | Only when route and tool capability authorize it | Detector or explicit project opt-in |
| `skills/domain` | Only when explicitly personal and provider-capable | Project evidence or explicit opt-in |
| `agents/agent-wide` | Always where custom agents are supported | Never |
| `agents/project-wide` | Never as personal-only content | Provider support plus detector/opt-in contract |
| `commands` | Only `route:agent` and provider support | Only `route:project` and provider support |
| `rules` | Provider-composed personal baseline | Provider-composed project baseline |

An unsupported combination is reported as `UNSUPPORTED`, never silently
skipped and never rendered as a different artifact type.

## Physical projection law

- The repository source is the only writable authority.
- Destinations contain independent physical files. No symlink, bind mount,
  cross-repository include, absolute source path, or runtime source lookup is
  allowed.
- Copy uses reflink when supported and falls back only to a normal physical copy
  on the same authorized destination contract; semantic content remains
  identical.
- Every managed output records source type, slug, digest, adapter version, and
  destination in an ownership manifest generated from discovery.
- Apply removes a stale output only when the prior manifest proves ownership.
  Foreign, unknown, symlinked, or locally modified content is preserved and
  makes the apply fail for operator resolution.
- The second unchanged apply must produce zero semantic and filesystem changes.

Project content is portable and generic. It must not teach development workflows
specific to this repository, AI Hub, Beads, Gas City, or a foreign repository.
Conditional technology/framework/tool/domain content is included only from
evidence inside the target project; no central project-name allowlist replaces
detectors.

FLEXT remains a future source for FLEXT projects. This increment imports or
projects no FLEXT-owned skill. A later approved import must adopt physical
content into the declared owner/destination contract without symlinks,
cross-repository references, or a second synchronizing writer.

## Root cutover

`~/.agents` remains the active checkout throughout semantic migration. After all
earlier phases are integrated and no process has an open file or current working
directory under it, the owner moves physically to `~/agents`.

The cutover rewires every supported consumer and removes the old path. It does
not leave a compatibility symlink, path alias, cross-repository reference,
dual-read loader, or fallback. Provider directories named `.agents` may exist
inside projects only as independent projections; they are never the personal
source owner.
