---
description: proxy, runtime, sessions, quota, safety
---

# Proxy operations fail closed

Proxy implementation and service operations are outside the current
`.agents`-only increment. Do not run a repair, restart, credential rotation, or
configuration mutation through this rule.

When a later explicitly authorized task operates the proxy:

- discover the current owner/configuration instead of assuming a port or path;
- preserve live sessions and obtain operator authority before a disruptive
  action;
- treat authentication, quota, HTTP 402/429, missing model, timeout, and
  transport errors as red;
- never reroute to another account/provider/model, degrade silently, fabricate
  capacity, or use a cached success as current proof;
- validate the exact selected model and real tool-using request after the owner
  change, then run native gates.
