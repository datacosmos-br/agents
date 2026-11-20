# Runtime runbook: model pipeline, hooks, and install (measured 2026-09-27)

Canonical procedures for the recovery steps live in `skills/domain/runtime-heal/`
and the startup contract in `commands/governance/session-preflight.md`. This
runbook records the measured proof chains, endpoints, and failure surfaces an
operator or recovery session needs at effect time. A recovery that deviates
from a chain below records the deviation and its evidence on the bead.

## Measured topology

- CLIProxy management API: `http://127.0.0.1:3184` (config snapshot PUT/DELETE,
  compare-and-swap publication target).
- CLIProxy inventory API: `http://127.0.0.1:8317/v0/management/model-inventory`
  (the live inventory the pipeline reads once per cycle).
- Pipeline state: `~/.local/state/ai-hub/model-pipeline/active.json` (the
  active publication `make install` hard-requires).
- Deployment root: `~/.local/share/ai-hub/runtime/current` → the activated
  release; units run `~/.local/bin/ai-hub` against it.
- models.dev catalog: ~0.46 s median for the 5.3 MB payload; the local TTL
  cache (6 h) removes it from per-cycle cost.

## Credential origins (ADR-0032 boundary)

The pipeline binds two proxy credentials at cycle time. The canonical shell
read is the user keyring, never an ambient export:

```sh
secret-tool lookup service ai-hub name PROXY_MANAGEMENT_SECRET
secret-tool lookup service ai-hub name PROXY_INTERNAL_API_KEY
```

A unit process is refused at `SecretToolKeyring.lookup` before `secret-tool`
spawns; environment-injected credentials resolve without a keyring touch. The
generated origin serves only the proxy key and only on a keyring miss.

## Pipeline chain (READY)

1. Deploy the release from a lane: `env -C <lane> -u INVOCATION_ID -u
   CREDENTIALS_DIRECTORY -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make install`
   (timeout 300 s).
2. Start: `systemctl --user start ai-hub-model-pipeline` (≤300 s). READY=1
   means one full cycle published: inventory load → probes (real PONG per
   route) → tiers → snapshot → PUT to the management API (CAS + projector
   verification) → consumers.
3. Proof: `active.json` exists; the snapshot `generation` advanced;
   `ai-hub status` reports the pipeline green.

Failure surfaces (each names its layer; never hand-strip):

| Surface | Layer | Owner |
| --- | --- | --- |
| `RepublishRequiredError` at bootstrap | provenance drift | tolerated by design: the fresh publication the drift demands IS the bootstrap cycle |
| `CLIProxy inventory JSON is invalid` | emitter contract mismatch | align the model or the emitter; an unstamped dev binary declares `built_at: "unknown"` (accepted sentinel, ADR-0035 lineage) |
| `no direct models` | CLIProxy inventory empty | fork owner |
| `httpx.ReadTimeout` | network | cache client at the owner |
| `ValidationError` | contract mismatch | align the model or the emitter |
| CCS HTTP 400 `built_at must be a UTC RFC3339 timestamp` | the running binary rejects the provenance it emits | CCS build/deploy channel: stamp the build or accept the sentinel |

## Binary provenance contract

`binary_provenance` travels with the inventory and the snapshot. A released
build stamps the UTC-Zulu instant; a dev build declares the literal
`"unknown"` instead of a fabricated date. A binary swap invalidates the
inventory's binary provenance: run the provenance reset (management API
`DELETE /api/config/model-pipeline`, operator-authorized) after swapping,
before starting the pipeline.

## Bootstrap deadlock (documented, do not improvise)

`make install` hard-requires the pipeline active publication, and the unit
runs the currently activated release. When the activated release cannot
publish (for example, it predates a routing cure), the documented order
cannot cross: reset provenance → start → install fails at the probe. The
authorized recovery is the foreground daemon from the cure-carrying code with
keyring-read credentials, run just long enough to publish, then `make
install` takes over and the unit is started. Record the recovery on the bead
with the captured commands.

## Hooks chain (OpenMoat)

OpenMoat owns agent hooks, policy packs, stdio MCP gating and audit logs (ai-hub
ADR-0030 hooks cohort and ADR-0045 OpenMoat amendment; Bead `aihub-wzj8i`). AI Hub no
longer declares a hook daemon or socket unit.

1. `openmoat status --format json`: per-agent protection level, `hook_warnings`,
   `lock_drift`, `mcp_changes`. An agent that disables the engine's entries (for
   example Codex `[hooks.state] enabled = false`) runs unchecked until a person
   enables them in the agent.
2. `openmoat doctor --format json`: lock, hooks, sandbox, MCP and binary integrity.
3. `openmoat show --recent N --format json` and `openmoat why --last`: the decisions
   real agent calls produced; no decision means no hook ran.
4. Operator-only interactive terminal actions when `doctor` or `status` reports drift:
   - `openmoat mcp accept ai-hub`: accept updated MCP server and tool pins.
   - `openmoat sandbox sync`: synchronize OS sandbox profiles (requires OpenMoat
     `>= 0.22.1` on Linux so Codex profiles exclude `/run/user` deny globs).
   - `openmoat policy trust-key` and `openmoat policy install <pack>`: install signed
     policy packs; `openmoat trust` enables a repository's `.moat/policy.yaml`.
   - `openmoat policy check-diff`: verify diff compliance before PR merge.
   - `openmoat audit anchor` and `openmoat provenance`: record closure evidence.

## Install idempotence

`make install` twice: the second run must produce a ZERO diff (no state
change, no receipt rewrite). Any diff is a defect in the install lifecycle,
never normalized away.

## Proxy session safety

The CCS/cliproxy process is a long-running managed daemon: never
`systemctl stop`/`disable` it, never edit its configuration while it reads
them, and never restart it without a recorded operator authorization.
