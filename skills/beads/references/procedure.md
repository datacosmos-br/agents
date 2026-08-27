# Beads

Use Beads as the shared project task system. Local plans, scratch files, and personal memories are useful, but they are not the durable source of truth for project work.

## First Step

Run:

```bash
bd prime
```

If that prints nothing, check whether the repository has an active Beads workspace:

```bash
bd where
```

## Preferred Route

Use the `bd` CLI when shell access is available. It is the most compact and direct Beads interface.

## Core CLI Workflow

1. Find work:

```bash
bd ready
bd list --status=open
bd list --status=in_progress
```

2. Inspect before editing:

```bash
bd show <id>
```

3. Claim work atomically:

```bash
bd update <id> --claim
```

4. Create durable follow-up work when implementation reveals new tasks:

```bash
bd create "Short title" --description="Why this exists and what needs to be done" --type=task --priority=2
```

5. Close completed work:

```bash
bd close <id> --reason="Completed"
```

## What Belongs In Beads

Use Beads for:

- shared project tasks
- blockers and dependencies
- discovered follow-up work
- work that must survive thread reset, compaction, or handoff
- status that another person or agent should be able to resume

Use agent-local planning tools only for the current turn's execution checklist. Do not treat them as shared project state.

## Rules

- Do not create markdown TODO files as the source of truth when Beads is available.
- Do not use `bd edit`; it opens an interactive editor. Use `bd update` flags instead.
- Prefer `--json` when parsing `bd` output programmatically.
- If hooks are installed, `bd prime` may already be injected. Run it manually when context is missing.
- Do not auto-close or mutate tasks unless the work is actually complete.

## Gas Town Canonical Doctrine (P0)

**Workspace placement:** Beads identifies the work; Gas Town owns where its
checkout exists. For a new repository use `gt rig add <rig> <git-url>`. For a
persistent operator workspace use `gt crew add <name> --rig <rig>`. For an
ephemeral agent lane use `gt sling <bead-id> <rig>`. Never use a raw clone or
manual worktree as a parallel execution surface. Never stage clones, database
copies, checkpoints, build trees, or audit reports in `/tmp`.

**Locator / DB routing:** único Dolt server `:3307`; **um db por rig** via `routes.jsonl` (`routing.mode: explicit`, SSOT `~/.gt/mayor/rigs.json`):

| rig | prefix | server db |
|-----|--------|-----------|
| town | hq | hq |
| gastown | gtf | gastown |
| aihub | aihub | aihub |
| agents | ag | agents |
| flext / dcdoc / cosmos / ccs / cliproxyapi / gmn / invest / mcb | flext / dcdoc / cosmos / ccs / cl / gmn / invest / mcb | (mesmo nome) |

- `bd where <id>` is the canonical locator. Use
  `bd -C <resolved-workspace-root> <cmd>` to select a ledger explicitly. Never
  use `bd --global` for project work.
- `bd list --include-infra --all --flat` (infra `agent/role/rig/message` é *hidden* por default!).
- `gt dolt` lifecycle: `start/stop/status/restart`(0-downtime)/`sql`(REPL, **sem `-e`**). Nunca escrever no server durante flap (PID steady ≥60s).

**Never invent flags** — run `<command> --help` for the installed version.
`bd create --deps` and `gt agents state` may exist, but their availability does
not make them the canonical workflow. Prefer `bd link` for explicit dependency
edits and `bd set-state` for durable issue dimensions.
- Reparent in-process (mesmo db, não-fecha): `bd update --parent <epic> <id>` +`--assignee`+`--append-notes`.
- `gt bead move <id> <prefix>` = copy + **CLOSE** source (`bead.go:35-38`) — **PROIBIDO em vivo**; Mayor P0 live (ex.: `gtf-chd`) → co-track: `bd link gtf-chd hq-cv-dg34w` + `bd set-state gtf-chd mode:co-tracked` + `bd update --parent <epic> gtf-chd --append-notes` (Owner/assignee Mayor preservados).
- Cross-deps: `bd link <a> <b>` (`--type blocks|related|parent-child`). State: `bd set-state <id> <dim:val>`.

> A tabela `routes.jsonl`/`rigs.json` acima substitui qualquer "intuição" de prefixo→db. Verifique `gt dolt status` + `bd where` antes de qualquer write.
