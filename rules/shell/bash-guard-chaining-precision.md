---
description: Bash Guard Chaining Precision
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-28","route:both"]'
---

# Bash Guard Chaining Precision

Top-level shell composition is bounded by operator code family. `&&` and `&`
each count as one use of code `&`; `||` and `|` each count as one use of code
`|`. A command may contain at most one top-level use of each code, so one `&`
family operator and one `|` family operator may coexist, but a second operator
from either same family is denied. Every resulting command segment remains
governed independently; composition never exempts a segment or its arguments
from any Bash guard.

Top-level `;` and newline remain denied. Any other top-level composition syntax
outside the two declared families is denied.

The sole semicolon exception is a pure `export` statement containing one or more `NAME=value` assignments, followed by exactly one top-level `;` and exactly one nonempty governed command.

Leading assignments and configured command wrappers never hide the governed executable. Every Bash guard applies to that executable and its arguments.

Quoted or escaped operator characters are command data, not shell composition.
Redirection operators, including `&>` and `&>>`, are redirections rather than
uses of either composition family and do not contribute to their cardinality.

Exports that execute command, backtick, or process substitutions are denied. Malformed exports and shell syntax are denied.
