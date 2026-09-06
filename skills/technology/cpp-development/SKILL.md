---
name: cpp-development
description: 'c++, build systems, modern development'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:CMakeLists.txt","detect:marker:compile_commands.json","detect:marker:conanfile.py","detect:marker:conanfile.txt","detect:marker:meson.build","detect:marker:vcpkg.json","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","technology:cpp","updates:manual","usage:router"]'
---

# C++ Development

Read `the procedure` (skill file) before changing C or C++ source,
headers, build definitions, ABI, ownership, concurrency, or native tests.

Use the standard, toolchain, dependency manager, build graph, formatter, static
analysis, and test framework declared by the project. Do not replace them with a
preferred stack. Preserve ABI and generated-source ownership unless the request
explicitly changes those contracts.
