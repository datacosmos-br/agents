# Workflow: declarative GitOps/Kubernetes change

## Goal

Correct desired state at its repository owner and let the declared reconciler
apply it. Live mutation is never a substitute for source correction.

## Procedure

1. Read repository law, architecture, ownership, environment scope, and the
   declared GitOps command surface.
2. Observe desired-versus-live state through read-only repository facades.
   Record exact application/resource identity, status, events, and decisive
   error without secrets.
3. Trace the defect to the owning values, template, manifest, schema, policy, or
   generator.
4. Change the canonical source. Never hand-edit generated output.
5. Render and validate through repository-native commands. Check schema,
   policy, selectors, references, generated drift, and second-run fixed point.
6. Land by approved PR and merge commit into the configured integration branch.
7. Observe reconciler health through the declared read-only facade and prove no
   remaining drift.

## Prohibited

- Direct live edit, patch, delete, forced sync, manual secret write, or emergency
  bypass.
- Suppression, ignored warning, hardcoded environment value, or old/new
  coexistence.
- Raw clone, manual worktree, symlink, cross-repository reference, or project
  state under `/tmp`.
- Claiming success from a local render without post-merge reconciler evidence.

If production recovery requires authority outside this contract, stop and give
the operator the exact failing command, exit/status, owner, impact, and required
decision. Do not execute the bypass.

Tracker runtime is suspended; update the repository-declared manual ledger and
do not call the phase `DONE`.
