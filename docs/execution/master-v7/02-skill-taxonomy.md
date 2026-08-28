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

## Migration and current catalog map

The migration started from 85 flat skills and reached the following 76 retained
targets. Two later operator-authorized governance capabilities were added after
that cutover: `plan-focus-recovery` for preserving active-plan intent across
detours and `fix-forward-collaboration` for concurrent adoption and anti-rollback
coordination. The current catalog therefore contains 78 skills. The table is an
acceptance map, not a runtime registry; recursive discovery from paths and tags
remains the runtime owner.

| Target group | Retained target slugs |
|---|---|
| `agent-wide` | `agent-introspection-debugging`, `prompt-safety-review`, `anti-phase-skip`, `article-writing`, `brand-voice`, `caveman`, `content-engine`, `context-canary`, `crosspost`, `deep-research`, `dispatch-agent`, `fix-forward-collaboration`, `frontend-slides`, `governance-audit`, `human-writing-style`, `investor-materials`, `investor-outreach`, `make-check`, `market-research`, `operator-correction-learning`, `plan-focus-recovery`, `safe-delete`, `skill-governance`, `sprint-closure`, `strategic-compact`, `summarization`, `verification-loop`, `video-editing` |
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
  aihub.tags: '["activation:detected","detect:marker:go.mod","provenance:agents-owned","route:project","technology:go","updates:manual","usage:router"]'
```

Allowed axes:

| Axis | Cardinality | Allowed examples |
|---|---:|---|
| `usage` | exactly one | `usage:router`, `usage:on-demand`, `usage:frozen` |
| `updates` | exactly one | `updates:manual`, `updates:forbidden` |
| `provenance` | exactly one | `provenance:agents-owned`, `provenance:vendor` |
| `route` | exactly one for conditional groups; absent from wide groups | `route:agent`, `route:project` |
| `activation` | exactly one for conditional groups; absent from wide groups | `activation:detected`, `activation:detected-or-opt-in`, `activation:opt-in` |
| detector | required by conditional activation | `detect:marker:go.mod`, `detect:dependency:npm:react`, `detect:owned-extension:.py`, `detect:owned-glob:src/**`, `detect:opt-in:scope-code-navigation`, `detect:selected-tag:tool:mcp` |
| primary subject | one or more for conditional groups | `technology:go`, `framework:react`, `tool:context7`, `domain:mle` |
| other semantic facet | optional | `role:verification`, `mode:review`, `lens:security` |

Path-derived invariants:

- `agent-wide` and `project-wide` derive distribution only from their paths;
  `route:*`, `activation:*`, and `detect:*` are forbidden there.
- Every conditional group requires exactly one route, one activation, and at
  least one subject in its own path namespace.
- `activation:detected` and `activation:detected-or-opt-in` require a non-opt-in
  detector. `activation:opt-in` and `activation:detected-or-opt-in` require an
  explicit `detect:opt-in:*` tag.
- `usage:frozen` and `updates:forbidden` must occur together; every other valid
  bundle is manually updated.
- Subject tags may overlap. Directory placement follows the skill's primary
  runtime dependency, not an arbitrary desire to balance counts.
- Unknown prefixes, duplicate tags, unsorted arrays, missing detector evidence,
  and path/tag contradictions fail discovery.

## Descriptions and progressive disclosure

Descriptions are comma-separated discovery metadata: 3-10 unique lowercase
keywords or nominal phrases, 12-96 characters total, with terms separated by
exactly `, `. Prose and copied activation instructions are invalid. Authored
routers state when to activate and when not to activate, stay concise, and
reference local procedures rather than duplicating them. A normalizer may
report an oversized router but cannot invent its semantic boundary. Procedures,
scripts, and assets remain inside the bundle and use relative local references.

Waza BPE counts enforce the skill-specific router and procedure policies.
Whitespace word counts are invalid. A budget violation fails validation; it is
never repaired by truncation, automatic rewriting of forbidden content, or
moving prose into another unvalidated file.

## Import boundary

No external artifact is copied, forked, synchronized, or translated during this
increment. After the current 78-skill set is integrated and green, a separately
approved import plan may compare official/provider-curated sources against this taxonomy.
That future plan must deduplicate first, audit provenance/license/scripts, and
adopt content physically into the same semantic layer without leaving an
updater or foreign runtime owner.
