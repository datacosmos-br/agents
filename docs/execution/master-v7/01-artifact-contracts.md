# Artifact contracts

## Type boundaries

| Type | Activation | Content | Canonical source | Validation owner |
|---|---|---|---|---|
| Rule | Always or path scoped | Non-negotiable constraint | `rules/` and universal instruction owners | Rule composition and contradiction gates |
| Skill | Model-selected or automatically applicable capability | Small router plus local procedure, references, scripts, and assets | `skills/<group>/<slug>/SKILL.md` | Skill schema, semantic Waza scenarios, BPE budgets |
| Command | Explicit user invocation by name | Parameterized workflow or prompt; may be long | `commands/<slug>.md` | Command schema, argument renderer, provider adapter, runtime eval |
| Agent | Explicit or delegated executor | Persona, tool boundary, capabilities, routing policy | `agents/<distribution>/<slug>.md` | Agent schema, capability and delegation evals |
| Hook | Declared event | Bounded deterministic reaction | Hook/config owner | Event, timeout, idempotence, and failure-propagation tests |
| CLI/script | Explicit deterministic execution | Typed I/O and side effects | Source/config owner | Unit, integration, runtime, static, and security gates |

Provider behavior never changes the canonical type. If a provider represents a
command with a mechanism also used for skills, the adapter still receives a
`CommandSpec`, applies command validation, and emits a command projection. It
must not convert that source into a canonical skill.

## Skill contract

- A skill supplies reusable model behavior and can be selected without an
  explicit slash invocation when its description matches the task.
- `SKILL.md` is a concise activation router. Detailed procedure lives in local
  `references/`; executable helpers and assets remain local to the bundle.
- Skill descriptions contain a compact comma-separated discovery vocabulary:
  3-10 unique lowercase keywords or nominal phrases within 12-96 characters.
  Activation and non-activation boundaries belong in the authored router; tags
  own catalog facets and distribution evidence.
- Skill routers and procedures use BPE token measurement. The command budget is
  never applied to them.
- A skill never embeds a slash-command usage contract, positional argument
  grammar, exact terminal table template, or provider command field.

## Command contract

- Canonical provider commands under `commands/` are authored prompt/workflow
  artifacts. They are distinct from the deterministic `agentsctl` runtime CLI.
- A command runs only after explicit invocation by its public name.
- Its picker description is short; its body may contain a complete workflow,
  argument contract, examples, validations, and output schema.
- Command bodies are not subject to the skill router or procedure limits. An
  adapter must either render the complete command within the provider's
  documented limit or fail loudly; truncation is forbidden.
- Mutating commands are manual-only and validate missing or ambiguous arguments
  before effects.
- Commands remain flat at the canonical source. Namespaces are provider
  projection details only when they preserve the approved public slug.

## Runtime CLI contract

`agentsctl` is the sole deterministic runtime entry point. Its complete public
grammar is exactly one required verb from `help`, `doctor`, `check`, `sync`,
`evaluate`, `secure`, `clean`, or `live`. No verb accepts an option, positional
argument, mode, format selector, compatibility alias, or private function path.

Each verb loads its typed SSOT and validates every required environment value,
source, destination, provider capability, child-process prerequisite, and
publication condition before its first effect. The first exception escapes with
raw traceback and causal chain. The CLI and its orchestrators do not catch or
normalize workflow failures. Make may compose development gates by calling this
public facade; it cannot duplicate runtime behavior.

## Rule and agent contracts

- Rules own mandatory behavior. A skill may reference a rule by stable local
  contract but must not duplicate it as another writable policy.
- Agents own execution boundaries and capabilities. They do not own universal
  engineering rules, technology guidance, provider credentials, or model
  selection.
- Agent documents inherit composed rules through the projection owner; repeated
  prompt-defense or engineering-law blocks are generated projections, not
  independently edited copies.
- No agent declares a model. The final live phase inherits the single model
  owner, exact `aihub-primary`.

## Discovery and ownership

Discovery is recursive and derives identity, type, distribution, and primary
group from path and validated frontmatter. No JSON or Python registry may list
artifact names, categories, destinations, or activation modes. Configuration may
declare only provider capabilities, output roots, schemas, and policy budgets.

Generated indexes and locks are disposable outputs. `skills.lock.json` is the
sole skill inventory lock; it contains source digests, rejects manual edits, and
converges on the second unchanged generation. Generated outputs never become
discovery sources.

## Type correction rule

When content is in the wrong surface:

1. classify it from observed activation and I/O behavior;
2. create exactly one canonical artifact of the correct type;
3. rewire its current consumers and semantic tests;
4. remove the misclassified source and stale projections in the same change;
5. reject the old route explicitly;
6. run contradiction, projection, and runtime gates.

Do not keep an old skill beside a new command, create aliases, or add a dual-read
period.
