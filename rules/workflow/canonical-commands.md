# Run agent functions only through the optionless CLI

`agentsctl` is the sole agent-runtime facade. Its complete public surface is
`help`, `doctor`, `check`, `sync`, `evaluate`, `secure`, `clean`, and `live`.
Each invocation contains exactly one verb and no option, positional argument,
mode, format selector, alias, or compatibility syntax.

Make is development support and gate composition. A Make target that needs
runtime behavior invokes one public `agentsctl` verb; it never imports a private
runtime function, reconstructs orchestration, or creates a second API.

A broken or out-of-pattern command is a defect to fix at its owner and rerun
through the same surface. Bypasses are blocking violations, not warnings. While
the tracker is suspended, preserve the exact blocker in Git/PR/CI evidence and
keep the repository-declared manual ledger current and the phase open.
