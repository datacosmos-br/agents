---
description: Running any ccs / cliproxy command (doctor, cliproxy start/restart). Load before touching the CCS proxy so live opencode sessions are not killed.
---

# Do not run ccs commands that recycle the proxy mid-session

`ccs doctor --fix` and `ccs cliproxy` restarts cycle the CLIProxy on :8317 and
kill live opencode sessions (a `--fix` was interrupted and dropped active
sessions). Do not run them while sessions are active; warn the operator first.

- Live in-proxy 429 cooldowns are not shown by `ccs ... quota`; fill-first can
  route to a rate-limited account. Treat transient upstream 429/quota as
  retry-and-degrade, never a hard task failure.
