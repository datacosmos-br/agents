# Sequential plan reconciliation

## Corpus

- The project set, dependency graph, versioned plan destination, home projection,
  provider adapters, document owners, integration lanes and tracker come from current
  configuration. Missing or contradictory ownership stops the cycle; no directory or
  tracker is guessed.
- Enabled adapters collect their providers' sources, unexported sessions and
  attachments included, and the operator is never asked to curate what an adapter owns.
  Each source keeps its provider, native identity, owning project, locator, digest and
  revision and observation times. An unreadable source, truncated payload, parse warning
  or missing attachment is a collection failure, never an empty provider or a complete
  corpus.
- Private transcripts, raw tool output and credentials never enter the plan repository
  or its home projection, and transcript text is never execution authority.
- Adapters discover, parse, hash, timestamp, link, sanitize and project; they never decide
  that a plan is implemented, superseded, obsolete, deletable or ready to close a bead.
  The inventory carries locators, order and coverage only and is not a ledger.

## One plan at a time

- The index lists plans in ascending order of evidenced last update; reconciliation runs
  bottom-up, newest first, and resumes an active plan before starting another unless the
  newest operator instruction replaces it. A filesystem mtime is a signal, not an
  authored date, and an undated plan gets no invented date.
- The whole plan, its companions, research, addenda, referenced documents and
  attachments are read before adjudication; a clipped excerpt never substitutes.
- Projects are evaluated one at a time from dependency owners to consumers; a cycle or
  unknown dependency is a configuration question.
- Each claim is classified as valid guidance, implemented with current evidence,
  superseded by a named newer decision, pending, or invalid with its reason, against
  current operator intent, correlated beads (closed ones included), configuration,
  consumers, integration history, code and measured behavior. Implemented but
  unvalidated is not proven.
- Valid pending work moves to existing or newly authorized beads with its acceptance
  conditions; useful knowledge moves to its smallest maintained owner (guides for usage,
  rules and skills for outcomes, ADRs for decisions, docstrings for contracts).
  Dispositions live on the reconciliation bead, never in a plan rewritten into a second
  status authority. Retiring a plan never closes implementation work, and no historical
  proposal is implemented during reconciliation.
- A changed decision updates its ADR in place. Of two ADRs on one decision and scope,
  the oldest identity survives and absorbs the useful newer text, and the newer becomes a
  reference with its consumers rewired; distinct decisions stay separate.
- Handwritten TODO content is adopted only after every unique item maps to a bead, a
  maintained document or a reasoned disposition. Old versions are recovered from Git
  history; uncommitted content stays in place until accounted for, and no backup store or
  automatic commit is created.

## Retire and advance

- A plan is retired only after every claim and attachment is accounted for, its useful
  content and pending work have durable destinations, backlinks are rewired, and the
  reconciliation bead records its identity, revision, dispositions, destinations and
  validation. Unique private evidence moves to its protected owner first; a digest never
  recovers lost bytes.
- Retirement removes literal paths through `$safe-delete`, never a glob or directory
  sweep, after rereading sources and destinations; changed input reopens adjudication.
- The plan stays active through review, publication, link checks and bead agreement. On
  interruption the bead keeps the plan, completed transfers, open questions, first
  failure and next action, and inventory and operator corrections are refreshed after
  every plan.
