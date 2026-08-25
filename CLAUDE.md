<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: no bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence.
3. Beads first: claim/update bead before file write, shell, or multi-step work; update after every repo-state change.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate discipline: if a gate blocks, stop and escalate with the exact command/edit; never route around it.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Divergence: FF push rejected → integrate by cooperation: `git merge --no-ff` the integration base into your lane, resolve conflicts, revalidate, land. Never rebase or force-push a shared branch; never discard another actor's work.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# CLAUDE.md — ai-hub

Project-specific context for AI agents. The configured repository artifacts below own universal and project execution law. This file is the thin profile and routing layer.

## Universal Law Pointers

- **Inviolable law:** [`UNIVERSAL_CORE.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/UNIVERSAL_CORE.md)
- **Project execution law:** [`AGENTS.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/AGENTS.md)
- **Agent reading order:** `docs/guides/agent-guide.md`
- **Governance controls:** `docs/GOVERNANCE.md`

## Developer Profile

> Updated manually. Keep directives current.

| Dimension | Rating | Confidence |
|-----------|--------|------------|
| Communication | terse-direct | MEDIUM |
| Decisions | fast-intuitive | MEDIUM |
| Explanations | concise | MEDIUM |
| Debugging | fix-first | MEDIUM |
| UX Philosophy | backend-focused | MEDIUM |
| Vendor Choices | conservative | MEDIUM |
| Frustrations | scope-creep | MEDIUM |
| Learning | self-directed | MEDIUM |

**Directives:**

- **Communication:** Keep responses concise and action-oriented. Skip lengthy preambles. Match this developer's direct style.
- **Decisions:** Present a single strong recommendation with brief justification. Skip lengthy comparisons unless asked.
- **Explanations:** Pair code with a brief explanation of the approach. Keep prose minimal.
- **Debugging:** Prioritize the fix. Show the corrected code first, then optionally explain what was wrong. Minimize diagnostic preamble.
- **UX Philosophy:** Optimize for developer experience over visual design.
- **Vendor Choices:** Recommend well-established, widely-adopted tools with strong community support.
- **Frustrations:** Do exactly what is asked — nothing more. Never add unrequested features, refactoring, or "improvements". Ask before expanding scope.
- **Learning:** Point to relevant code sections and let the developer explore. Add signposts rather than full explanations.

## Context-Aware Routing

Apply this routing automatically before executing any substantial task:

1. Detect repository context using nearest markers.
2. Load project rules first, then only path-relevant skills. Avoid bulk-loading unrelated skills.
3. Use tool routing by task type:
   - Code navigation/search: structural navigation tools first, then fast text search.
   - Single-file edits: direct edit/patch tools.
   - Multi-file refactors: structural refactor tools or carefully scoped batched edits.
   - Validation: run project-native build/test/lint commands.
4. Use MCP only when context requires it and the server is configured.
5. Enforce tool guardrails by context:
   - No destructive git operations unless explicitly requested.
   - No broad filesystem deletes/rewrites without scope confirmation.
   - No network/external API calls for strictly local tasks.
   - No generated/vendor/cache tree edits unless the task explicitly targets them.

For FLEXT repositories, prefer path-scoped skills and follow the canonical load order from project `AGENTS.md`.

## Scope Guardrail

When working inside a repository, load that repository's `AGENTS.md` and `CLAUDE.md` for scoped rules.

## Issue Tracker

This project uses an issue tracker for execution state. Run the tracker prime command to see full workflow context.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use the tracker for ALL task tracking — do not use ad-hoc TODO lists.
- Run the tracker prime command for detailed reference and session close protocol.
- Use the tracker remember command for persistent knowledge — do not use memory files.

## Session Completion

1. **File issues for remaining work** — Create tracker items for anything that needs follow-up.
2. **Run quality gates** (if code changed) — Tests, linters, builds.
3. **Update issue status** — Close finished work, update in-progress items.
4. **Land git/sync by active profile**:

   ```bash
   git status
   git add <scoped-paths>
   git commit -m "<scope>: <summary>"
   git push
   git status
   ```

5. **Close or escalate** — Record validation, commit SHA, push output, issue status, and any real blocker.

**Critical rules:**

- Explicit user or orchestrator instructions override this block.
- Normal scoped commit and fast-forward push are authorized by the default profile after validation.
- If a required sync or push is blocked, record the exact command, exit code, and decisive output in the tracker before stopping.
