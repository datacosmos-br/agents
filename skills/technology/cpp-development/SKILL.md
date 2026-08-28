---
name: cpp-development
description: 'Develop modern C++ projects when local build markers prove a C++ toolchain.'
metadata:
  aihub.tags: '["activation:detected","detect:marker:CMakeLists.txt","detect:marker:compile_commands.json","detect:marker:conanfile.py","detect:marker:conanfile.txt","detect:marker:meson.build","detect:marker:vcpkg.json","provenance:agents-owned","route:project","technology:cpp","updates:manual","usage:router"]'
---

# C++ Development

Read [the procedure](references/procedure.md) before changing C or C++ source,
headers, build definitions, ABI, ownership, concurrency, or native tests.

Use the standard, toolchain, dependency manager, build graph, formatter, static
analysis, and test framework declared by the project. Do not replace them with a
preferred stack. Preserve ABI and generated-source ownership unless the request
explicitly changes those contracts.
