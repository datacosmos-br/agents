---
name: rtk
description: "rtk token economy, command output filtering, fleet routing"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0016","detect:opt-in:rtk","effective:2026-09-16","route:agent","subject:mcp","usage:on-demand"]'
---

# rtk

rtk (Rust Token Killer) is the fleet's command and output economy layer. Rewriting is
performed by rtk's own native hook: `rtk hook claude` as the Claude Code `PreToolUse`
Bash entry and `rtk hook cursor` for Cursor. AI Hub deploys those entries from its agent
SSOT as foreign adapters; it does not rewrite commands itself. `rtk rewrite <cmd>` is
rtk's single rewrite decision (exit 0 allow with the rewritten command, 1 no rewrite, 2
deny, 3 ask). This skill governs the manual surface, output analysis, and the
observability loop.

## USE FOR

- Any verbose or high-volume command output that feeds model context: `gh`, `glab`,
  `cargo`, `npm`, `pnpm`, `bun`, `deno`, `docker`, `kubectl`, `oc`, `aws`, `psql`,
  `dotnet`, `curl`, `wget`, `tsc`, `next`, `lint`, `prettier`, `prisma`, `playwright`,
  `jest`, `vitest`.
- Validation loops that must surface only signal: `rtk test <cmd>` (failures only),
  `rtk err <cmd>` (errors/warnings only) — exit codes still propagate.
- Reading and inspection economy: `rtk read`, `rtk ls`, `rtk tree`, `rtk grep`,
  `rtk find`, `rtk diff`, `rtk wc`, `rtk json [--keys-only]`.
- Long-output analysis: `rtk log <file>` (filter and deduplicate), `rtk summary <cmd>`,
  `rtk pipe -f <filter>` (filter stdin), `rtk smart`.
- Environment and dependency audits: `rtk env` (sensitive values masked), `rtk deps`
  (project dependency summary).
- Extreme context pressure: the global `--ultra-compact` flag.
- Fleet observability: `rtk gain [-f json]`, `rtk session`, `rtk discover`,
  `rtk cc-economics`.

## DO NOT USE FOR

- Git: git stays plain and is never prefixed with `rtk`. Claude Code worktree isolation
  refuses rtk-wrapped git (`rtk git …`) because the launcher hides the git verb, so AI
  Hub excludes `git` from the rewrite.
- The canonical Make dispatcher: `make` verbs stay canonical; rtk filters an approved
  output, it never replaces an owner verb.
- Hiding failures: a filtered failure is still a failure. Never present rtk output as
  success evidence; report exit codes and decisive output per law.
- Secrets: never place credentials in rtk-wrapped commands; `rtk env` masks output, it
  does not sanitize input.
- Auto-rewrite expectations for deferred constructs — heredocs, `$(...)` or backtick
  substitution, and file redirects are never rewritten (anti-launder design). Use the
  explicit manual form when one is needed.
- Hand edits of `~/.config/rtk/config.toml`: AI Hub owns it from its tools SSOT
  (`tools.rtk_config`, published by deploy). Its `[hooks] exclude_commands` lists `git`.
  A project-local `.rtk/filters.toml` requires explicit `rtk trust` authorization.

## Workflow

1. Prefer the automatic path: rtk's native hook already rewrites eligible Bash calls.
   Take no action.
2. For registry gaps and deferred constructs, prefix manually: `rtk <command>`.
3. Run a long or compound command through the agent's background execution with output
   written to `~/tmp/<scope>/<name>.log`, then analyze it with `rtk log <file>`,
   `rtk err <cmd>`, `rtk test <cmd>`, `rtk summary <cmd>`, or `rtk pipe -f <filter>`.
   Never chain `| head | tail`: the bash guard allows one `|`-family and one `&`-family
   operator at top level.
4. On failure, read the tee-recovery path referenced in the filtered output instead of
   re-executing the command.
5. When output still floods context, escalate once: add `--ultra-compact`, or narrow the
   underlying command — never pipe through ad-hoc truncation.
6. After a work session, measure: `rtk gain -d` (day), `rtk session` (adoption);
   investigate regressions with `rtk discover`.
7. A missing or failing binary is a typed boundary degradation (fail-open): continue
   natively, report `rtk --version` versus the `config.AiHub.tools` pin, and let the
   SSOT owner fix provisioning.

## Critical rules

- One binary owner: the pinned row in AI Hub `config/tools.yaml`. Never install a
  parallel rtk (cargo, brew, script) beside it; zero residue.
- Never re-implement rewriting inside an agent or a second hook chain: rtk's native hook
  is the rewrite owner and `rtk rewrite` its decision.
- Doctors stay green: `rtk init --show` and `rtk verify` require the literal
  `rtk hook claude` `PreToolUse` entry that AI Hub deploys.
- Telemetry stays disabled fleet-wide; audit is opt-in via `RTK_HOOK_AUDIT=1` during
  validation windows.
- Filters must use anchored `match_command` regexes (`^...$`) — unanchored patterns are
  rejected at load since rtk v0.48.
- A rewrite never changes semantics: only the command prefix moves to `rtk`; arguments,
  env prefixes and chained segments are preserved.

## Example

- Agent runs `docker ps` → rtk's native hook rewrites to `rtk docker ps` → compact
  container list.
- Agent runs `git status` → excluded from the rewrite; plain git runs.
- Agent runs `make test` in the background writing `~/tmp/lane/test.log`, then
  `rtk log ~/tmp/lane/test.log` → deduplicated failures; the make owner stays the
  executor and its exit code is reported.
- Failed verbose command → filtered output cites
  `~/.local/share/rtk/tee/<epoch>_<cmd>.log` → agent reads the tee file once instead of
  re-executing.

## Troubleshooting

- Rewrite did not happen: dry-run with `rtk rewrite "<command>"` or
  `rtk hook check --agent <agent> "<command>"`; exit 1 means no rtk equivalent or an
  excluded command (git) — run it plain or apply the manual form.
- Hook integrity: `rtk init --show` and `rtk verify` must both be green; fix a red
  result at the AI Hub agent SSOT and redeploy.
- Savings look zero: `rtk session` shows per-session adoption; `rtk discover` lists
  missed opportunities.
- Filter not applying: check anchoring, `schema_version`, and whether the project-local
  file is trusted (`rtk trust --list`).
- Binary mismatch: `rtk --version` must equal the declared pin; reinstall only through
  the canonical AI Hub provisioning path, never by hand.
