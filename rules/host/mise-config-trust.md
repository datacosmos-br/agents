---
description:
  mise trust is hash-based and resets on every config rewrite; persistent
  trust is path-based via settings, and fresh-bootstrap mise instances read
  ~/.config/mise/settings.toml — seed it, don't re-trust.
capsule_summary: |
  Measured 2026-09-26/27 on tungs: `mise trust <file>` records the file's
  hash; any rewrite of ~/.config/mise/config.toml (a sibling session, a mise
  self-update, `mise settings add`) silently un-trusts it again, and every
  shim invocation dies with "error parsing config file ... are not trusted".
  The durable fix is the trusted_config_paths SETTING, persisted in
  ~/.config/mise/settings.toml — path-based, rewrite-proof.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'th-based, not hash-based

## The two failure shapes this rule exists for

1. **Recurring untrust.** `mise trust <file>` records a hash; the next rewrite
   of `config.toml` resets it. Test shards then die on
   `mise ERROR ... are not trusted` at random times — the flake follows the
   rewrite, not your change.
2. **Pinned-HOME tests meet a fresh mise.** Tests that pin `HOME` to a temp
   dir while PATH resolves through mise shims download a fresh mise binary
   that reads `~/.config/mise/settings.toml` for settings. If that file does
   not exist, every shim dies with `No version is set for shim: <tool>` even
   though the interactive shell works.

## The durable fix

```bash
# once, as the host operator:
mise settings add trusted_config_paths /home/<user>/.config/mise
printf 'trusted_config_paths = ["/home/<user>/.config/mise"]\n' \
  > ~/.config/mise/settings.toml
```

Path-based trust survives every config rewrite and is read by both the
interactive mise and the fresh-bootstrap copies the test harness spawns.

## For test suites that pin HOME

Carry the manager state directories across the pin instead of trusting the
hash: `MISE_CONFIG_DIR` and `MISE_DATA_DIR` pointing at the real host
locations make shims resolve under a pinned HOME (see ai-hub
`testOwnedHome`, which does exactly this).
