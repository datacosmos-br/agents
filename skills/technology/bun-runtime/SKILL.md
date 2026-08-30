---
name: bun-runtime
description: 'bun runtime, javascript tooling, project detection'
metadata:
  aihub.tags: '["activation:detected","decision:plan-00","detect:marker:bun.lock","detect:marker:bun.lockb","effective:2026-08-28","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","technology:bun","updates:manual","usage:on-demand"]'
---

# Bun Runtime

Activate only when project markers or an approved migration select Bun. A
JavaScript or TypeScript source edit alone does not choose a runtime.

Before package, test, build, or run effects, resolve the declared Bun version,
lockfile, package/workspace owner, scripts, deployment runtime, native dependency
compatibility, required environment, output owner, and project gates. Missing or
conflicting evidence stops with zero effects.

Use only the declared Bun and script surfaces. Install from the lock without
updating it unless dependency change is authorized. Do not add Node, npm, yarn,
pnpm, another Bun version, alternate scripts, or compatibility commands as a
fallback path.

Preserve the first install, script, test, build, timeout, signal, or runtime
failure unchanged. Publish only the complete verified artifact through its owner;
remove candidates and obsolete lock/runtime paths. Report exact commands, exits,
decisive output, material artifact, and residue proof.
