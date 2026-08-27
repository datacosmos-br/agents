---
name: ralph-loop
description: ralph, loop, iterative, improvement, pattern, user, wants, quality, work, through
---

> ⛔ **LEI SUPREMA — RESOLVER, NUNCA ESCONDER (NO-BYPASS / ROOT-CAUSE-ONLY).** Esta skill é
> subordinada à lei suprema: defeito corrige-se na RAIZ e verifica-se verde — nunca mascarado,
> silenciado, contornado ou reportado verde sem verificação. Canônico: `~/.claude/AGENTS.md` §0.


# Ralph Loop

Agentic pattern: implement one task, verify with quality gates, commit if pass, repeat until done.

## Execution

### Per iteration

1. **Select** – Highest-priority incomplete task
2. **Search** – Prove the canonical origin and the native deletion primitive before editing
3. **Implement** – Single change (one task)
4. **Verify** – Run project quality checks (tests, linters, build)
5. **Commit** – If checks pass, suggest atomic commit (user approves)
6. **Update** – Mark task complete in progress file
7. **Document** – Note learnings for next iterations
8. **Continue** – Next task, or output `COMPLETE`

### Quality gates

Use project conventions: `make test`, `make lint`, `npm test`, `cargo test`, etc. Check for `Makefile`, `package.json`, `Cargo.toml`, or `README` to infer commands.

### Progress

Maintain a progress file (e.g. `ralph-progress.md` or `tasks.md`) with checkboxes and brief learnings.

## Rules

- One task per iteration
- Search before write: helper-first refactors are invalid until existing origins and native language/framework primitives are ruled out
- Prefer model-driven validation (`model_validate`, `TypeAdapter`, typed kwargs envelopes) over manual payload normalization
- Always run verification before marking done
- Fix failures before continuing
- Prefer small, atomic commits
