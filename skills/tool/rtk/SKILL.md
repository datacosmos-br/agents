---
name: rtk
description: 'rtk token economy, command output filtering, fleet routing'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0016","detect:opt-in:rtk","effective:2026-09-07","route:agent","subject:mcp","usage:on-demand"]'
---

# rtk

rtk (Rust Token Killer) is the fleet's command and output economy layer. The
ai-hub hook daemon rewrites eligible Bash commands through rtk before
execution (ADR-0029); this skill governs the manual surface, the deferred
constructs, and the observability loop.

## USE FOR

- Any verbose or high-volume command output that feeds model context: `git`,
  `gh`, `glab`, `cargo`, `npm`, `pnpm`, `bun`, `deno`, `docker`, `kubectl`,
  `oc`, `aws`, `psql`, `dotnet`, `curl`, `wget`, `tsc`, `next`, `lint`,
  `prettier`, `prisma`, `playwright`, `jest`, `vitest`.
- Validation loops that must surface only signal: `rtk test <cmd>` (failures
  only), `rtk err <cmd>` (errors/warnings only) — exit codes still propagate.
- Reading and inspection economy: `rtk read`, `rtk ls`, `rtk tree`,
  `rtk grep`, `rtk find`, `rtk diff`, `rtk wc`, `rtk json [--keys-only]`.
- Environment and dependency audits: `rtk env` (sensitive values masked),
  `rtk deps` (project dependency summary).
- Log triage: `rtk log` (filter and deduplicate).
- Summaries of arbitrary command output: `rtk summary <cmd>`, `rtk smart`.
- Extreme context pressure: the global `--ultra-compact` flag.
- Fleet observability: `rtk gain [-f json]`, `rtk session`, `rtk discover`,
  `rtk cc-economics`.

## DO NOT USE FOR

- The canonical Make dispatcher: `make` verbs stay canonical; rtk filters an
  approved output, it never replaces an owner verb. Fleet `make` filters live
  in the SSOT-rendered catalog, never in ad-hoc authoring.
- Hiding failures: a filtered failure is still a failure. Never present rtk
  output as success evidence; report exit codes and decisive output per law.
- Secrets: never place credentials in rtk-wrapped commands; `rtk env` masks
  output, it does not sanitize input.
- Auto-rewrite expectations for deferred constructs — heredocs, `$(...)` or
  backtick substitution, and file redirects are never rewritten (anti-launder
  design). Use the explicit manual form when one is needed.
- Out-of-fleet edits: `~/.config/rtk/config.toml` and `filters.toml` are
  SSOT-rendered projections; project-local `.rtk/filters.toml` requires
  explicit `rtk trust` authorization. Never hand-edit either.

## Workflow

1. Prefer the automatic path: the hook daemon already rewrites eligible Bash
   calls (Claude, Codex, Cursor, Kimi, OpenCode, Gemini). Take no action.
2. For registry gaps and deferred constructs, prefix manually: `rtk <command>`.
3. On failure, read the tee-recovery path referenced in the filtered output
   instead of re-executing the command.
4. When output still floods context, escalate once: add `--ultra-compact`, or
   narrow the underlying command — never pipe through ad-hoc truncation.
5. After a work session, measure: `rtk gain -d` (day), `rtk session`
   (adoption); investigate regressions with `rtk discover`.
6. A missing or failing binary is a typed boundary degradation (fail-open):
   continue natively, report `rtk --version` versus the `config.AiHub.tools`
   pin, and let the SSOT owner fix provisioning.

## Critical rules

- One binary owner: the mise-pinned row in `config/tools.yaml`. Never install
  a parallel rtk (cargo, brew, script) beside it; zero residue.
- Never re-implement rewriting inside an agent: native per-agent rtk hooks are
  stripped by design; the daemon chain is the only execution path.
- Telemetry stays disabled fleet-wide (`RTK_TELEMETRY_DISABLED=1`); audit is
  opt-in via `RTK_HOOK_AUDIT=1` during validation windows.
- Filters must use anchored `match_command` regexes (`^...$`) — unanchored
  patterns are rejected at load since rtk v0.48.
- A rewrite never changes semantics: only the command prefix moves to
  `rtk`; arguments, env prefixes and chained segments are preserved.

## Example

Fleet-shaped session fragment (auto-rewrite active):

- Agent runs `git status` → daemon chain rewrites to `rtk git status` →
  compact status with branch and entry counts.
- Agent runs `rtk test pytest -q` → only failures and the summary line;
  exit code preserved for the gate.
- Agent runs `rtk err make check` → only errors and warnings from the
  canonical verb; the make owner stays the executor.
- Failed verbose command → filtered output cites
  `~/.local/share/rtk/tee/<epoch>_<cmd>.log` → agent reads the tee file once
  instead of re-executing.

## Troubleshooting

- Rewrite did not happen: dry-run the engine with
  `rtk hook check --agent <agent> "<command>"`; passthrough (exit 1/2) means
  the command is outside the registry or uses a deferred construct — apply the
  manual form.
- Savings look zero: `rtk session` shows per-session adoption; `rtk discover`
  lists missed opportunities; confirm the daemon chain row exists in
  `config/hooks.yaml` rather than debugging the client.
- Filter not applying: check anchoring, `schema_version`, and whether the
  project-local file is trusted (`rtk trust --list`); global catalog rows come
  from the SSOT projection.
- Binary mismatch: `rtk --version` must equal the declared pin; reinstall only
  through the canonical provisioning path (`ai-hub generate-mise-config`),
  never by hand.
