---
globs: ["*.ts", "*.tsx", "**/*.ts", "**/*.tsx"]
---
# TypeScript Rules

> ⛔ **LEI SUPREMA — RESOLVER, NUNCA ESCONDER.** Prevalece sobre toda regra deste arquivo: defeito
> corrige-se na RAIZ e verifica-se verde — nunca `catch {}` vazio, `?? default` mascarando falha,
> `as any`, ou claim verde sem verificação. Canônico: `~/.claude/AGENTS.md` §0.

- Strict mode sempre (noImplicitAny, strictNullChecks)
- Use LSP diagnostics (typescript-language-server) após cada Edit
- Prefer `interface` sobre `type` para objetos (extensibilidade)
- Prefer `const` sobre `let` quando possível
- Use `make lint`, `make typecheck`, `make format` (não tsc/eslint direto)
- Async/await sobre .then() chains
