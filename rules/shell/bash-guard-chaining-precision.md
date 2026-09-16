---
description: Bash Guard Chaining Precision
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-16","route:both"]'
---

# Bash Guard Chaining Precision

Guards are precise, not broad: each denies one exact construct and never blocks
a command agents legitimately need (for example `gh pr merge --admin`).

Composition is counted at top level only, by operator code family. `&&` and `&`
each count as one use of code `&`; `||` and `|` each count as one use of code
`|`. A command may contain at most one top-level use of each code, so one `&`
family operator and one `|` family operator may coexist, but a second operator
from either same family is denied. Every resulting command segment
remains governed independently; composition never exempts a segment or its
arguments from any Bash guard.

Top-level `;` and newline remain denied. Any other top-level composition syntax
outside the two declared families is denied.

The sole semicolon exception is a pure `export` statement containing one or more `NAME=value` assignments, followed by exactly one top-level `;` and exactly one nonempty governed command.

Leading assignments and configured command wrappers never hide the governed executable. Every Bash guard applies to that executable and its arguments.

Quoted or escaped operator characters are command data, not shell composition.
Redirection operators, including `&>` and `&>>`, are redirections rather than
uses of either composition family and do not contribute to their cardinality.

Exports that execute command, backtick, or process substitutions are denied. Malformed exports and shell syntax are denied.

Do not build long pipelines such as `| head | tail`. Run a long or compound
command through the agent's background execution with output written to
`~/tmp/<scope>/<name>.log`, then analyze it with `rtk log <file>`,
`rtk err <cmd>`, `rtk test <cmd>`, `rtk summary <cmd>`, `rtk pipe -f <filter>`,
or rtk's tee recovery file (the `rtk` skill). Git stays plain, never prefixed
with rtk.
