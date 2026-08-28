---
name: scope-code-navigation
description: 'Trace code and references when scoped repository navigation is explicitly requested.'
triggers:
- reading a file to understand its structure
- searching for a function, class, or symbol
- finding references or callers
- before editing or refactoring code
- understanding dependencies or call chains
- exploring an unfamiliar codebase
- finding who calls a function
- checking blast radius before a change
- navigating code
- finding entry points or API controllers
- grep for function or class names
- understanding how code is structured
- looking at imports or dependencies
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:scope-code-navigation","provenance:agents-owned","route:project","tool:scope-code-navigation","updates:manual","usage:on-demand"]'
---

# Scope — Code Intelligence for LLM Agents

Scope is a CLI tool that gives you structural code intelligence without reading full source files. It extracts symbols, call graphs, and dependency relationships from the AST and stores them in a local index.

**Key insight from benchmarks:** Agents using Scope are 32% cheaper per task and make 67% more code edits per session. Scope doesn't reduce file reads — it makes every read count. Agents that understand the architecture finish in fewer turns.

## When to Use Scope

**Check first:** Run `scope status` at the start of any session. If a `.scope/` directory exists, Scope is available.

**Prefer Scope over grep/find when you need to:**

- Understand a class or function before editing it -> `scope sketch`
- Find who calls a function before changing its signature -> `scope callers`
- Search for code by what it does, not what it's named -> `scope find`
- Understand the repo architecture -> `scope map`
- Find entry points (API controllers, workers) -> `scope entrypoints`
- Check blast radius before a refactor -> `scope callers --depth 2`
- Trace how requests reach a function -> `scope trace`

**Do NOT use Scope when:**

- You already know the exact file and line to edit — just read the file
- You need the full source code to make an edit — `scope sketch` is not a substitute for reading
- The index is stale and you haven't re-indexed — run `scope index` first

## Decision Tree

```
New task arrives
    |
    +- Complex task (multiple files, unfamiliar code)?
    |      -> scope map                    # ~500 tokens, full repo overview
    |      -> then scope sketch <symbol>   # drill into specific classes
    |
    +- Need to find code by intent?
    |      -> scope find "<description>"   # search by what code does
    |
    +- Need to understand a class before editing?
    |      -> scope sketch <ClassName>     # ~200 tokens vs ~4,000 for source
    |
    +- Changing a function signature?
    |      -> scope callers <method>       # every call site with file + line
    |
    +- Debugging / tracing a bug?
    |      -> scope trace <symbol>         # entry-point-to-symbol paths
    |
    +- Need to find how A connects to B?
    |      -> scope flow <start> <end>     # call paths between any two symbols
    |
    +- Simple known-location edit?
           -> Just read the file directly
```

## Optimal Workflows (from 54 benchmark runs)

### Discovery — "Find X and modify it"

```
scope find "<description>"     -> Read target file -> EDIT
```

Total: 1 scope command + 1-3 reads. Do NOT sketch after find.

### Bug Fix — "X is broken, find and fix it"

```
scope trace <symbol>           -> Read suspected file -> EDIT
```

Total: 1 scope command + 2-3 reads. If you don't know the symbol, use `scope find` first.

### Refactoring — "Restructure X to pattern Y"

```
scope sketch <class>           -> Read target + related files -> EDIT
```

Total: 1 scope command + 3-5 reads. Sketch gives structure; read only files you'll modify.

### New Feature — "Build something integrating X, Y, Z"

```
scope map                      -> scope sketch <ServiceA>
                               -> scope sketch <ServiceB>
                               -> Read 1-2 pattern files -> EDIT
```

Total: 1 map + 2-4 sketches + 1-2 reads. This is Scope's sweet spot — 17-30% token savings.

### Cross-cutting change — "Update across multiple services"

```
scope callers <method>         -> Read each call site -> EDIT each
```

Total: 1 scope command gives you every file to change. No need for grep.

## Command Reference

| Command | What it returns | Tokens | When to use |
|---------|----------------|--------|-------------|
| `scope map` | Entry points, core symbols, architecture layers | ~500-1000 | Start of complex tasks |
| `scope sketch <symbol>` | Methods, modifiers, deps, caller counts | ~200 | Before editing a class |
| `scope callers <symbol>` | Every caller with file, line, snippet | varies | Before changing signatures |
| `scope callers <sym> --depth 2` | Transitive callers grouped by depth | varies | Blast radius analysis |
| `scope refs <symbol>` | All references by kind (calls, imports, extends) | varies | Complete reference audit |
| `scope find "<query>"` | Symbols matching intent, ranked by relevance | varies | Finding code you can't name |
| `scope trace <symbol>` | Entry-point-to-symbol call paths | varies | Bug tracing |
| `scope flow <start> <end>` | Call paths between any two symbols | varies | Understanding how A connects to B |
| `scope entrypoints` | API controllers, workers, event handlers | varies | Understanding request flow |
| `scope deps <symbol>` | What this depends on | varies | Understanding prerequisites |
| `scope rdeps <symbol>` | What depends on this | varies | Before deleting/renaming |
| `scope status` | Index health, symbol count, freshness | small | Check before querying |
| `scope index` | Refresh the index (incremental, < 1s) | — | After editing files |

## The 3-Command Rule

If you've run 3 scope commands and haven't edited a file yet, **stop navigating and start editing**. Benchmark data shows agents that follow this rule use 30% fewer tokens.

## Anti-Patterns

1. **Don't sketch what you'll immediately read** — sketch replaces reading, not precedes it
2. **Don't run `callers` AND `refs`** for the same symbol — callers is a subset of refs
3. **Don't run 5+ scope commands** on any task — you're over-navigating
4. **Don't default to grep when `scope find` fits better** — find searches names, signatures, callers, and file paths
5. **Don't skip `scope map`** on complex tasks — one call replaces 5-17 file reads for orientation
6. **Don't ignore line numbers** in scope output — they point you exactly where to read/edit

## Workspace Support

If you see a `scope-workspace.toml` file, the project spans multiple directories:

```bash
scope workspace list                    # see all member projects
scope map --workspace                   # architecture across all projects
scope refs <symbol> --workspace         # find references across all projects
scope find "<query>" --workspace        # search across all projects
```

Use `--project <name>` to target a specific member without changing directory.
