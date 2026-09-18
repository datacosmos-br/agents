# React component procedure

## Preflight

Resolve project law, React/runtime versions, client/server boundary, renderer and
router, component consumers, state/data owner, design system, accessibility and privacy
contracts, package/lock owner, generated surfaces, public behavior, runtime, and native
gates before effects. Missing or conflicting evidence stops with zero code or external
effects.

## Minimal owner decisions

- Compose components around one current behavior and keep state at its narrowest real
  owner. Derive values during render instead of duplicating state.
- Use an effect only to synchronize an external system. Declare complete stable
  dependencies and return cleanup for timers, subscriptions, listeners, requests, and
  other owned resources.
- Define async ownership, cancellation, ordering, and publication before starting work.
  A typed domain rejection may render as declared UI state; a thrown I/O or framework
  failure remains causal and is not caught into empty data, a warning, retry, fallback
  component, or alternate request.
- Parse external data at the existing boundary. Never log or transmit credentials or
  sensitive input, and never add analytics, tracking, or third-party sinks without
  explicit owner approval.
- Preserve semantic HTML, labels, keyboard behavior, focus order, live-region semantics,
  reduced motion, and the project's responsive/design tokens.
- Memoize, split, virtualize, or add a dependency only after a current measured
  render/bundle/interaction defect proves the need. Keep the project framework and
  state/data owners; do not introduce a generic hook, context, store, or library.

## Proof

Rewire affected consumers atomically and remove obsolete effects, state, props, logs,
dependencies, fixtures, and component paths. Exercise material UI behavior, typed
rejection, thrown first failure, cancellation/unmount cleanup, accessibility, privacy,
and measured performance through the public runtime and native gates. Report exact
owners, code removed, commands/exits/output, zero effects, and zero residue.
