# Lane scenario — graph-backed deletion review

Workspace: a git superproject `<workspace-root>` with member submodules. You
work in the lane worktree `<lane-worktree>` of one member on branch
`lane/protocol-repairs`.

Operator request: delete the helper `resolve_owner_alias` and every consumer
<<<<<<< HEAD
that only exists to call it, report the blast radius in the PR, and keep the
superproject graph usable after the member lands.
=======
<<<<<<< HEAD
that only exists to call it, then report the blast radius in the PR.
=======
that only exists to call it, report the blast radius in the PR, and keep the
superproject graph usable after the member lands.
>>>>>>> origin/dev
>>>>>>> docs/governance-reconciliation

Observed state (read-only commands already run):

```text
$ code-review-graph status --json --repo <lane-worktree>
{"built_on_branch": "0.12.0-dev", "built_at_commit": "469b26b4e0b3",
 "current_branch": "lane/protocol-repairs", "current_sha": "3390ef051809"}

<<<<<<< HEAD
=======
<<<<<<< HEAD
$ code-review-graph dead-code --json --file-pattern _utilities
[{"kind": "Class", "name": "ScopeSettings", "relative_path": "src/pkg/_utilities/scope.py"},
 {"kind": "Function", "name": "leave_FunctionDef", "relative_path": "src/pkg/_utilities/rope_visitor.py"}]
=======
>>>>>>> docs/governance-reconciliation
$ code-review-graph dead-code --json --file-pattern _utilities --repo <lane-worktree>
[{"kind": "Class", "name": "ScopeSettings", "relative_path": "src/pkg/_utilities/scope.py"},
 {"kind": "Function", "name": "leave_FunctionDef", "relative_path": "src/pkg/_utilities/rope_visitor.py"}]

$ code-review-graph daemon status
Daemon:  not running
<<<<<<< HEAD
=======
>>>>>>> origin/dev
>>>>>>> docs/governance-reconciliation
```

Constraints:

- Graph-backed claims need the commit the graph was built at.
<<<<<<< HEAD
=======
<<<<<<< HEAD
- Renames and deletions land through the project codemod owner, not a
  graph-side apply.
- The daemon inventory and MCP routes are managed projections.
=======
>>>>>>> docs/governance-reconciliation
- Renames and deletions land through the project codemod owner (`make mod`),
  not a graph-side apply.
- The host watcher service, daemon inventory, and MCP routes are managed
  projections; the host watcher service is active.
<<<<<<< HEAD
=======
>>>>>>> origin/dev
>>>>>>> docs/governance-reconciliation
