---
description: Python environments are physical and checkout-local
metadata:
  aihub.tags: '["decision:ADR-0025","effective:2026-09-22","route:both"]'
---

# Python environments are physical and checkout-local

Use the repository's declared setup owner and interpreter. `make setup` provisions only
`<workspace>/.venv`, a physical directory exclusively owned by that workspace. A worktree
is its own workspace; its environment never resolves to the primary checkout.

- Never borrow another checkout's environment through a symlink, path dependency,
  `PYTHONPATH`, editable-install path, or cross-repository reference.
- Never place the environment outside that workspace, install another repository as an
  editable dependency, or let inherited environment variables route setup or execution
  to another environment. Setup owns the checkout-local environment identity.
- Caches and temporary artifacts remain outside the checkout; they are not Python
  environments and must never become environment-sharing paths.
- Never replace or clear a real environment while another process may own it.
- Every manual task uses a dedicated Git worktree and branch, including while Gas City
  orchestration is suspended. Provision that worktree's own physical environment
  through its canonical setup surface; never implement in the primary/default checkout
  or borrow its environment. Suspension does not forbid native Git worktrees.
- Missing or stale environment state is red. Repair it through the repository's
  canonical setup surface only when that mutation is authorized.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
