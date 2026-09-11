# Instruction-layer design: how rules, capsules, skills, and events shape agent behavior

**Version:** 1.0
**Last updated:** 2026-09-10
**Author:** delivery-contract program (bead ag-p4a, WS-D)
**Related:** `docs/adr/ADR-0017`, `docs/adr/ADR-0018`, `docs/adr/ADR-0019`, `docs/adr/ADR-0020`
**Status:** Evidence document. Records measured/external findings only; it is
never current architecture and never an authority (precedence: ADRs > docs).

## Executive summary

Fourteen authoritative sources (vendor engineering guidance, provider
references, and peer-reviewed work) converge on the mechanisms that make
instruction-layer components — system prompts, capsules, rules, skills,
commands, lifecycle hooks, and memory — reliably steer agent behavior:
explicit authority chains, small high-signal context delivered at the right
altitude, progressive disclosure through skills, verifiable instructions,
executable verification loops, and externalized state across compaction.
This dossier grounds ADR-0017..0020 decisions; each section maps findings to
the artifact that owns them here.

## 1. Authority resolution (→ engineering-core, operator-precedence)

- Instructions are ranked in an explicit chain of command; a later
  instruction at the same level supersedes an earlier one; quoted text, tool
  outputs, and multimodal data carry no authority by default ([OpenAI Model
  Spec](https://model-spec.openai.com/2025-04-11.html)).
- Conflicts resolve by focusing on the higher-level authority and the overall
  purpose; ambiguity triggers stating assumptions and asking clarifying
  questions (ibid.).
- **Local mapping:** the capsule carries the precedence order; `advance`
  Phase 0 resolves authority before any effect.

## 2. Prompt structure effects (→ capsule budget, advance phrasing)

- Three agentic reminders — persistence ("keep going until completely
  resolved"), tool use before guessing, and explicit planning between tool
  calls — raised SWE-bench Verified pass rates by ~20% in combination
  ([GPT-4.1 prompting guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)).
- On instruction conflict, the instruction closer to the end of the prompt
  tends to win; for long context, instructions belong at both beginning and
  end (ibid.).
- Over-emphasis backfires: emphasizing everything emphasizes nothing; bloated
  instruction files cause rules to be ignored
  ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)).
- Relevant information placed in the middle of long context is recalled
  significantly worse than at the boundaries ([Lost in the
  Middle](https://arxiv.org/abs/2307.03172)).
- Instruction adherence is measurable when instructions are verifiable
  programmatically ([IFEval](https://arxiv.org/abs/2311.07911)).
- **Local mapping:** non-negotiables restated at the end of `advance`; the
  typed capsule budget gate (ADR-0019) keeps the always-on payload inside
  the 10,000-character hook ceiling; gate evidence is programmatic.

## 3. Progressive disclosure and skills (→ skill routing, advance)

- Skills deliver procedural knowledge in three disclosure levels: name and
  description in the system prompt, the skill body on demand, bundled files
  only when needed ([Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)).
- Effective system prompts sit at the "right altitude" — concrete enough to
  steer, general enough to avoid brittle if-else — and context is curated to
  the smallest set of high-signal tokens ([Effective context
  engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- **Local mapping:** `advance` routes each phase to its owning skill and
  never inlines skill bodies; stack deltas stay in branch-matched law skills.

## 4. Continuity: resume, compaction, memory (→ advance Phases 1-2, ADR-0019 events)

- Long-horizon coherence comes from compaction, structured note-taking, and
  sub-agent architectures; compaction quality is judged by recall of
  critical state, not by brevity ([Context
  engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- Memory tools plus context editing improved agentic-search performance by
  39% and cut token consumption by 84% in 100-turn evaluations ([Managing
  context](https://claude.com/blog/context-management)).
- Virtualized memory tiers let an agent page state in and out across sessions
  ([MemGPT](https://arxiv.org/abs/2310.08560)).
- Verbal reflection stored in episodic memory improved subsequent-trial
  accuracy (91% vs 80% on HumanEval) ([Reflexion](https://arxiv.org/abs/2303.11366)).
- Production agents resume from checkpoints instead of restarting; orchestrators
  persist their plan to memory before it can be truncated ([Multi-agent
  research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)).
- **Local mapping:** `advance` Phase 1 restores the seven-item state from
  bead + Git; Phase 2 is the Reflexion checkpoint; ADR-0019's `post-compact`
  payload reserves room for the restore list.

## 5. Verification and orchestration (→ advance Phases 3-5)

- Agents need a check they can run: "looks done" is not a signal; evidence
  (command, exit code, output) beats assertion; a fresh-context reviewer
  evaluates the result on its own terms ([Claude Code best
  practices](https://code.claude.com/docs/en/best-practices)).
- Principles plus a critique-and-revision feedback loop steer behavior with
  little supervision ([Constitutional AI](https://arxiv.org/abs/2212.08073))
  — the organizational analogue is findings routed by guarantees to owner
  artifacts.
- Delegation needs objective, output format, tool guidance, and boundaries;
  explicit effort-scaling rules prevent overinvestment; heuristics outperform
  rigid rules ([Multi-agent research
  system](https://www.anthropic.com/engineering/built-multi-agent-research-system)).
- Simple composable patterns beat frameworks; agents need ground truth from
  the environment at each step ([Building effective
  agents](https://www.anthropic.com/engineering/building-effective-agents)).
- **Local mapping:** `advance` Phases 3-5; the guarantee map is the
  critique-revision routing table (ADR-0011).

## 6. Lifecycle events (→ ADR-0019 delivery contract)

- Providers expose typed lifecycle events with matchers and JSON decisions:
  `SessionStart` (startup/resume/clear/compact/fork), `UserPromptSubmit`,
  `PreToolUse`/`PostToolUse`, `SubagentStart`/`Stop`, `Stop`,
  `PreCompact`/`PostCompact` (manual/auto), `InstructionsLoaded`
  (session_start/include/compact), `SessionEnd` ([Hooks
  reference](https://code.claude.com/docs/en/hooks)).
- Hooks are deterministic guarantees; instructions are advisory. Both exist;
  they are not substitutes.
- **Local mapping:** the `delivery` contract publishes the event→payload map
  as validated data so the runtime renders hooks from the bundle, never from
  prose (ADR-0008 boundary).

## Sources

1. [OpenAI Model Spec 2025-04-11](https://model-spec.openai.com/2025-04-11.html) — chain of command, untrusted data, letter-and-spirit.
2. [GPT-4.1 prompting guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide) — agentic reminders, recency, structure workflow.
3. [Claude Code best practices](https://code.claude.com/docs/en/best-practices) — verification loops, CLAUDE.md hygiene, review, context management.
4. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow patterns, ACI, ground truth.
5. [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — attention budget, altitude, compaction, note-taking, sub-agents.
6. [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — progressive disclosure levels, skill authoring.
7. [Multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) — delegation contracts, effort scaling, heuristics.
8. [Hooks reference](https://code.claude.com/docs/en/hooks) — lifecycle event catalog and decision schemas.
9. [Managing context](https://claude.com/blog/context-management) — measured effects of memory + context editing.
10. [IFEval](https://arxiv.org/abs/2311.07911) — verifiable instruction categories.
11. [Lost in the Middle](https://arxiv.org/abs/2307.03172) — positional degradation.
12. [Reflexion](https://arxiv.org/abs/2303.11366) — verbal reinforcement across trials.
13. [MemGPT](https://arxiv.org/abs/2310.08560) — virtual context management.
14. [Constitutional AI](https://arxiv.org/abs/2212.08073) — principles plus critique-revision feedback.

## Methodology

Operator-directed deep research (2026-09-10): 14 sources fetched in full via
webfetch across five sub-questions — authority resolution, prompt-structure
effects, skills/progressive disclosure, continuity/resumption, and
verification/orchestration. Every design implication above points at the
local owner that absorbs it; this document proposes nothing.
