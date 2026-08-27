# Agent Workflows — Implementation Playbooks

Each file in this directory is a **complete, copy-pasteable workflow** for a specific task type. No manual command lookup required.

## Quick Reference

| Task Type | File | Projects | Key Command |
|-----------|------|----------|-------------|
| Bug Fix | `bug-fix.md` | flext, mcb, cosmos-main | `make check && make test` |
| New Feature | `feature.md` | flext, mcb, cosmos-main | `make check && make test && make val` |
| Refactor | `refactor.md` | flext, mcb | `make check && make test` |
| Documentation | `docs.md` | All | `make docs` |
| GitOps / K8s | `gitops.md` | cosmos-main | `make check && make sync` |
| Emergency Fix | `hotfix.md` | All | `git diff + make check + commit` |

## Project Detection

The agent should auto-detect the project type by checking for these files:

```bash
# FLEXT (Python monorepo)
[[ -f "pyproject.toml" && -d "flext-core" ]] → PROJECT=flext

# MCB (Rust workspace)
[[ -f "Cargo.toml" && -d "mcb-domain" ]] → PROJECT=mcb

# DataCosmos (K8s/GitOps)
[[ -d "apps" && -d "makefiles" && -f "Makefile" ]] → PROJECT=cosmos-main
```

## Universal Validation Gate

After **every** edit, run the project-specific validation:

```bash
# FLEXT
make check WHAT=fmt,types,lint && make test

# MCB
make check WHAT=fmt,lint,validate && make test

# cosmos-main
make check WHAT=quick,validate,scripts
```

If any gate fails, **fix before continuing**. No exceptions.

## Pre-Session Checklist

Before starting any implementation:

1. `git status` — understand current state
2. `git branch` — confirm you're on the right branch
3. `make check WHAT=coordination` — beads/bd status
4. Read the project's `AGENTS.md` and `CLAUDE.md`
5. Check for `.continue-here.md` or `CONTINUATION-*.md` files

## Post-Session Checklist

Before ending any session:

1. `git diff` — review all changes
2. Run the universal validation gate (above)
3. `make check WHAT=coordination` — update beads status
4. If changes are complete and validated, ask user about commit
5. Never leave uncommitted changes without a bead tracking them

## Workflow Principles

- **SSOT**: Universal governance lives here; typed runtime and MCP configuration lives in AI Hub.
- **MCP Sync**: Run `make mcp`; it delegates generation and validation to the installed `ai-hub` owner.
- **Evidence**: Every claim needs command output + exit code
- **No manual commands**: If a step requires a command, it should be in this workflow
- **Blocked ops**: When R10 applies (blocked operation), hand exact command to user
