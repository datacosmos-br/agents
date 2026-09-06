---
name: nextjs-turbopack
description: 'next.js, turbopack, frontend performance'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:dependency:npm:next","effective:2026-08-28","framework:nextjs","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","tool:turbopack","updates:manual","usage:on-demand"]'
---

# Next.js and Turbopack

Activate only when the detected Next.js project and requested path involve its
bundler, cache, development startup/HMR, or production build behavior.

Before effects, resolve the pinned Next.js version, package/lock owner, scripts,
config/plugins, selected bundler for each command, deployment contract, cache and
artifact owners, current error, official documentation for that exact release,
baseline measurements, and native gates. Missing evidence stops with zero effects.

Change only the script/config owner that explicitly selects the wrong path. Do
not guess flags, delete `.next`, add a Webpack/Turbopack alternate after failure,
upgrade versions, change routers/components, or enable analyzers without a current
requirement and compatibility proof.

Measure cold start, HMR, unchanged restart/cache reuse, and production build as
separate contracts. Preserve the first command failure unchanged and publish no
partial artifact. Report the material script/config change, measurements, exact
commands/exits/output, cache identity, and zero residue.
