---
description: Every command has one wall-clock deadline, a timeout is incomplete failure, and profiling is opt-in
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-11-02","route:both"]'
---

# Command deadline and performance

Every command, including setup, full suites and profiling, has a 120-second
wall-clock bound covering activation, preflight, locks, children and termination.
Wrap unenforced entrypoints without changing operation/scope, suppressing output
or normalizing failure.

Use the Make owner's native deadline runner. Where enforcement is absent, the
external form is `timeout --signal=TERM --kill-after=<reserve>s <work-budget>s make <verb>`;
work budget plus termination reserve must fit the declared total bound. Shared locks
use bounded `flock -w <seconds>`. Resolve both values from the selected owner, never
freeze a sibling's reserve or add a second budget (operator order 2026-10-24, tracker memory
`operator-order-2026-10-24-make-always-with-timeout`).

Reserve termination time inside the 120-second total bound: TERM begins no later than
total minus reserve, and all owned children terminate within that total. Nested
operations consume the remaining invocation budget,
never a fresh child budget. Do not signal another actor's process or remove its lock
to obtain the window.

A timeout is incomplete failure. Preserve output, exit, completed scope and profile.
Correct its measured cause before repeating; no unchanged retry, higher limit,
unbounded background job, idle slow-run queue or false complete receipt assembled
from partial outputs.

Profile slow Python generation/migration through the root Make operation's declared
opt-in cProfile binding. Repair missing bindings at their owner; never invent targets,
aliases, private invocations or old capture configuration. Bind captures to source,
runtime, configuration and scope; separate wall/cumulative time and parent waits/child
work. Reuse native capture, receipt and analysis owners, never parallel
metadata/cache/scanner/engine machinery. Invalid caller edges block optimization;
native thread/process ownership must cover elected workers. Missing child captures
prove no zero CPU. Repair one measured cause, revalidate public behavior and compare
the same operation before scaling.
Native locked executable lookup consumes the configured tool request directly,
never a reconstructed command-line version request. Repair invalid lookups at
their command/template owner before repeating setup/upgrades. Never disable
locked mode, parse native locks or borrow host executables.
Upgrade moving Mise requests with native `lock --bump`, not plain refresh retaining
the previous resolution. Setup remains locked and never advances locks.
Gate placement and opt-in instrumentation follow
[`gate-budget.md`](gate-budget.md).

Workflow source proves native deadline-runner binding; unwrapped recipes prove no
enforcement. Documentation-only work records missing enforcement without editing
excluded code or claiming it implemented.

Compose with `rules/workflow/canonical-commands.md`, which owns the command surface,
and `rules/workflow/gate-budget.md`, which owns gate placement.
