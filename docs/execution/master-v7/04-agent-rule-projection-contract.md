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
- `activation:always|detected|detected-or-opt-in|opt-in`
- `detect:*` when conditional

No target count is permitted. Discovery must fail on an undecided duplicate or
ambiguous responsibility rather than force it into a balanced category.

Provider-native custom-agent projection is enabled only where the provider
documents both a physical destination and a complete capability allowlist:

| Provider | Personal destination | Project destination | Status |
|---|---|---|---|
| Claude | `~/.claude/agents` | `.claude/agents` | Supported |
| GitHub Copilot CLI | `~/.copilot/agents` | `.github/agents` | Supported with Copilot-owned YAML frontmatter and tool aliases |
| Gemini CLI | `~/.gemini/agents` | `.gemini/agents` | Supported |
| OpenCode | `~/.config/opencode/agents` | `.opencode/agents` | Supported |
| Codex, Cursor, Antigravity | none | none | `UNSUPPORTED` until a complete native capability contract is proved |

An empty canonical tool list renders an explicit empty provider allowlist. It
never omits the field and thereby expands to a provider's all-tools default.

Custom-agent adapter evidence:

- [GitHub Copilot custom-agent schema and tool aliases](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
  and [CLI destinations](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli);
- [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/);
- [OpenCode agents](https://opencode.ai/docs/agents/);
- [Antigravity skill destinations](https://antigravity.google/docs/skills).

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
separate document compiler. It owns one digest-verified managed region and
preserves all surrounding foreign content. Codex, Gemini, OpenCode, and the
Antigravity global surface use this compiler. Antigravity project item rules
remain `UNSUPPORTED` because the official docs name activation modes but do not
publish file metadata that preserves path-scoped semantics.

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

An unsupported combination is a declarative non-target in the capability
matrix. `sync` applies every `SUPPORTED` authorized project cell and never
requests an `UNSUPPORTED` cell or renders it as another artifact type. The same
invocation applies every supported personal cell.

The project target is the nearest ancestor of the invocation cwd that owns a
physical `.git/` directory; the personal target is the current process home.
Unowned worktree `.git` files, symlinked metadata, target
arguments, environment overrides, and alternate personal modes are rejected or
absent by construction.

Optional activation is project-owned at `.agents/projection.json`. If present,
the v1 object has exactly `version`, sorted unique `opt_ins`, sorted unique
`selected_tags`, and sorted unique `agents`. Unknown values raise before any
effect. A v2 object adds an optional `detection_rules` array: each rule has an
`id` (`[a-z0-9-]+`), a `when` object holding exactly one of `all`/`any`/`none`
over filesystem conditions (`path_exists`, `path_missing`, `file_contains`,
`file_not_contains` with `pattern`, plus `paths` for file-content scopes), and
`activate_tags` matching the same tag grammar as skills. Satisfied rules merge
their tags into `selected_tags`, activating `detect:selected-tag:` skills
declaratively with no code. The source repository itself is never a projection
target and therefore carries no selection file. The same physical file
authorizes tracked project projection; if absent, the project is a non-target
and no detector or project surface is loaded. The
generated v5 manifest records portable project identity (`.`), project-relative
destination, context, surface, providers, selection, source type, slug,
activation evidence, logical digest, physical digest, and adapter version.

Canonical project detection is a typed contract in
`agents_governance.projection_config`. A matching association marker authorizes
one minimal v3 selection containing its closed project profile and the digest
of the complete detection catalog; `sync` creates or refreshes it, while
`check` remains read-only and rejects stale or contradictory evidence. The
document is portable project source. Provider settings, hook scripts, and
other derived projection destinations remain runtime state and are never
source.

## Physical projection law

- The source package is the only catalog authority; the current process home
  and invocation project are the only projection destinations.
- Destinations contain independent physical files. No symlink, bind mount,
  cross-repository include, absolute source path, or runtime source lookup is
  allowed.
- Generated hook commands never embed an absolute destination path; each
  provider/context pair resolves its script from that provider's documented
  root token, and an undefined pair fails the projection.
- One physical copy implementation owns staging and publication. Failure raises;
  no second strategy is attempted.
- Every managed output records source type, slug, digest, adapter version, and
  destination in an ownership manifest generated from discovery.
- Apply removes a stale output only when the prior manifest proves ownership.
  Non-conflicting foreign physical content is preserved without adoption.
  A foreign collision, symlink, or locally modified managed output is preserved
  and makes the apply fail for operator resolution.
- The second unchanged apply must produce zero semantic and filesystem changes.
- Every target is preflighted before staging. All changed targets are staged on
  their destination filesystem before publication. A later target failure
  rolls earlier publications back and re-raises the original exception with
  any rollback failure attached.
- Provider hooks are generated delivery adapters, never policy owners or public
  commands. Exact, equivalent, advisory, and unsupported lifecycle boundaries,
  native event names, and client scope are typed in the matrix and recorded in
  hook manifests.

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

`~/agents` is the active checkout and the canonical physical owner. The
predecessor path is retired: no consumer may resolve the owner through it, and
no process may hold an open file or current working directory under it.

The cutover rewires every supported consumer and removes the old path. It does
not leave a compatibility symlink, path alias, cross-repository reference,
dual-read loader, or fallback. Provider directories named `.agents` may exist
inside projects only as independent projections; they are never the personal
source owner.
