---
globs: ["*.rs", "**/*.rs", "Cargo.toml"]
---
# Rust Rules

> ⛔ **LEI SUPREMA — RESOLVER, NUNCA ESCONDER.** Prevalece sobre toda regra deste arquivo: defeito
> corrige-se na RAIZ e verifica-se verde — nunca `unwrap_or_default()` para mascarar falha, `let _ =`
> em `Result`, ou claim verde sem verificação. Canônico: `~/.claude/AGENTS.md` §0.

- Use `make build`, `make test`, `make lint` (não `cargo` direto, exceto `cargo build`/`cargo check`/`cargo doc`/`cargo run` que estão no allow list)
- Use rust-analyzer LSP para navigation e diagnostics
- Prefer `?` operator sobre match chains para error handling
- Lifetime annotations explícitas quando o compiler pedir
- Use `#[derive(...)]` para traits comuns (Debug, Clone, PartialEq)
- Documentar public API com `///` doc comments
