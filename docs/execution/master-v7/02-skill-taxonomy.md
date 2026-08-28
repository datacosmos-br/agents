# Skill taxonomy and migration map

## Directory contract

```text
skills/
├── agent-wide/
├── project-wide/
├── technology/
├── framework/
├── tool/
└── domain/
```

The first two names are distribution contracts, not vague audiences:

- `agent-wide`: always installed in every authorized personal agent home and
  never projected into projects.
- `project-wide`: always installed in every authorized project projection and
  never installed as a personal-only capability.

The remaining groups are conditional semantic families:

- `technology`: language, runtime, compiler, or ecosystem; detector required.
- `framework`: framework or platform layer; dependency/marker detector required.
- `tool`: product, protocol, service, or explicit operational tool; detector or
  project opt-in required.
- `domain`: specialist business or engineering domain independent of stack;
  project evidence or explicit opt-in required.

Each skill has one canonical directory. A skill that touches several subjects
uses multiple tags; it is never copied into several groups.

## Current migration map

The migration starts from 85 flat skills. The target contains the following 76
skills. The table is a semantic map for this one cutover, not a permanent
registry; after migration, recursive discovery from paths and tags replaces it.

| Target group | Retained target slugs |
|---|---|
| `agent-wide` | `agent-introspection-debugging`, `prompt-safety-review`, `anti-phase-skip`, `article-writing`, `brand-voice`, `caveman`, `content-engine`, `context-canary`, `crosspost`, `deep-research`, `dispatch-agent`, `frontend-slides`, `governance-audit`, `human-writing-style`, `investor-materials`, `investor-outreach`, `make-check`, `market-research`, `operator-correction-learning`, `safe-delete`, `skill-governance`, `sprint-closure`, `strategic-compact`, `summarization`, `verification-loop`, `video-editing` |
| `project-wide` | `anti-hardcode`, `rest-api-design`, `architecture-documentation`, `backend-patterns`, `code-review-expert`, `config-schema-migration`, `data-modeling-analysis`, `doc-drift`, `documentation-criteria`, `dry`, `eval-harness`, `extermination-mode`, `fail-fast`, `product-capability`, `search-first`, `security-review`, `simplify`, `solid`, `ssot`, `tdd-workflow`, `technical-writing-style`, `yagni` |
| `technology` | `bun-runtime`, `cpp-development`, `go-development`, `jvm-development`, `python-development`, `python-parallelization`, `rust-development`, `typescript-development` |
| `framework` | `flutter-development`, `react-frontend-patterns`, `nextjs-turbopack` |
| `tool` | `agent-browser`, `beads`, `beads-orchestrator`, `beads-worker`, `scope-code-navigation`, `context7-documentation`, `dmux-workflows`, `playwright-e2e`, `exa-search`, `fal-ai-media`, `gascity-change-lifecycle`, `gascity-workspace-lifecycle`, `mcp-server-patterns`, `openspec-verify-change`, `pr-sheriff`, `x-api` |
| `domain` | `mle-workflow` |

### Renames

| Current slug | Target slug | Reason |
|---|---|---|
| `ai-prompt-engineering-safety-review` | `prompt-safety-review` | The capability is prompt safety review, not a provider or registry identity. |
| `api-design` | `rest-api-design` | The current procedure is REST-specific. |
| `code-navigation` | `scope-code-navigation` | The procedure owns scoped repository navigation, not all code intelligence. |
| `documentation-lookup` | `context7-documentation` | The current procedure depends on the Context7 tool contract. |
| `e2e-testing` | `playwright-e2e` | The current procedure is Playwright-specific. |
| `frontend-patterns` | `react-frontend-patterns` | The current procedure is React-specific. |
| `skill-creator` | `skill-governance` | Avoid collision with provider/system skill creators and state the local governance role. |

Renames are atomic. All local references, eval names, projection manifests, and
generated destinations change in the same commit. Old slugs do not remain as
aliases.

### Convert to commands

These six artifacts expose explicit command invocation, argument, scaffold, or
terminal-output behavior and move to `commands/<slug>.md`:

- `add-language-rules`
- `database-migration`
- `feature-development`
- `ghi-list`
- `pr-list`
- `ralph-loop`

The migration preserves useful workflow content but rewrites it against the
[command contract](03-command-contract.md). No same-name skill survives.

### Remove as skills

- `coding-standards`: move any unique enforceable rule to its rule owner and any
  unique reusable procedure to the relevant existing skill, then delete the
  duplicated bundle.
- `inviolable-rules`: universal law remains in `AGENTS.md`/`rules/`; a selectable
  skill must not duplicate mandatory policy.
- `sequential-thinking`: remove the arbitrary reasoning scaffold; it neither
  owns project behavior nor a provider-independent capability.

Deletion requires a content-level search. Unique behavior cannot be discarded,
but duplicated wording cannot justify retaining a second owner.

## Tag grammar

Tags are local frontmatter metadata stored as a deterministic sorted JSON array:

```yaml
metadata:
  version: "1.0.0"
  aihub.tags: '["activation:detected","detect:marker:go.mod","route:project","technology:go","usage:router"]'
```

Allowed axes:

| Axis | Cardinality | Examples |
|---|---:|---|
| `route` | exactly one for conditional groups; derived for the two wide groups | `route:agent`, `route:project` |
| `activation` | exactly one | `activation:always`, `activation:detected`, `activation:opt-in` |
| detector | one or more when detected | `detect:marker:go.mod`, `detect:dependency:react`, `detect:command:waza` |
| subject | one or more | `technology:go`, `framework:react`, `tool:context7`, `domain:mle` |
| usage | one or more where relevant | `usage:router`, `usage:procedure`, `usage:review` |
| risk | optional, one primary value | `risk:read`, `risk:write`, `risk:external` |

Path-derived invariants:

- `agent-wide` implies `route:agent` and `activation:always`; contradictory
  frontmatter fails validation.
- `project-wide` implies `route:project` and `activation:always`.
- `technology` and `framework` require `activation:detected` plus a detector.
- `tool` and `domain` require a detector or `activation:opt-in`.
- Subject tags may overlap. Directory placement follows the skill's primary
  runtime dependency, not an arbitrary desire to balance counts.
- Unknown prefixes, duplicate tags, unsorted arrays, missing detector evidence,
  and path/tag contradictions fail discovery.

## Descriptions and progressive disclosure

Descriptions are short discriminating sentences that answer “what capability”
and “when to use it.” Raw keyword lists move to tags. Routers stay concise and
reference local procedures rather than duplicating them. Procedures, scripts,
and assets must remain inside the bundle and use relative local references.

Waza BPE counts enforce the skill-specific router and procedure policies.
Whitespace word counts are invalid. A budget violation fails validation; it is
never repaired by truncation, automatic rewriting of forbidden content, or
moving prose into another unvalidated file.

## Import boundary

No external artifact is copied, forked, synchronized, or translated during this
increment. After the 76-skill set is integrated and green, a separately approved
import plan may compare official/provider-curated sources against this taxonomy.
That future plan must deduplicate first, audit provenance/license/scripts, and
adopt content physically into the same semantic layer without leaving an
updater or foreign runtime owner.
