# Bash Guard Chaining Precision

Top-level `;` and newline are denied. Top-level ampersand and pipe operators
are counted by code-base: `&&` and `&` each consume one `&` use; `||` and `|`
each consume one `|` use. At most one use of each code-base is accepted, and a
second use of the same code-base is denied.

Every accepted segment is independently subject to the complete guard. A
permitted composition never hides a blocked executable, Git operation, shell
spawn, output destruction, relocation, or other governed behavior.

The sole semicolon exception is a pure `export` statement containing one or more `NAME=value` assignments, followed by exactly one top-level `;` and exactly one nonempty governed command.

Leading assignments and configured command wrappers never hide the governed executable. Every Bash guard applies to that executable and its arguments.

Quoted or escaped operator characters are command data, not shell chaining.

Exports that execute command, backtick, or process substitutions are denied. Malformed exports and shell syntax are denied.
