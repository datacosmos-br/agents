# Strict Atomic Configuration Schema Migration

## Scope and authority

Use this procedure for any configuration schema, serialized representation,
environment mapping, generated projection, validator, or loader contract change.
Repository and operator rules outrank this procedure.

A change to a public interface is prohibited before implementation unless the
operator has reviewed and explicitly approved the exact proposed contract,
affected users, breaking behavior, and cutover plan. An issue, ADR, test, or prior
implementation is not a substitute for operator approval.

## Non-negotiable invariant

A migration is one atomic cutover. The same reviewed change must:

1. change the canonical schema and its typed models;
2. transform every persisted configuration and generated source;
3. rewire every producer, loader, validator, consumer, test, example, command,
   service, deployment, and document;
4. regenerate every managed projection from its owner;
5. delete the superseded schema, fields, routes, files, fixtures, code paths, and
   terminology; and
6. prove the new contract through native gates and real runtime consumers.

Never retain the old and new contracts together. Compatibility shims, aliases,
fallback readers, dual writes, silent defaults, deprecation windows, feature
flags, suppressions, stubs, and hardcoded translations are prohibited.

If every known user cannot be rewired in the same change, stop before editing.
Split preparatory internal refactors only when they do not alter the contract and
do not introduce dormant or parallel behavior.

## Workflow

### 1. Establish the owner and impact graph

- Read repository law, ADRs, config owners, schemas, generators, loaders, and
  runtime entry points.
- Search all related repositories for field names, environment variables,
  serialized keys, defaults, examples, fixtures, and generated copies.
- Enumerate producers, stored instances, consumers, and deployment/runtime users.
- Identify the canonical integration branch and native PR/gate workflow.
- Record the migration and acceptance evidence in the canonical tracker. If the
  tracker is unavailable, stop tracker writes and report the exact failure; never
  invent durable state.

### 2. Gate public interfaces

Before changing a public interface, present the operator with:

- exact old and proposed contracts;
- affected users and repositories;
- data transformation and removal plan;
- expected breaking behavior; and
- validation and rollback boundaries.

Do not implement until explicit approval is recorded. Internal schema changes may
proceed only when repository evidence proves they are not publicly observable.

### 3. Design the atomic cutover

- Define one final schema; there is no transitional schema.
- Define a deterministic, fail-loud transformation for existing data.
- Make migration idempotent: rerunning on the final state produces no change.
- Validate the complete output before replacing persistent data. Use the owning
  database/config transaction or repository-approved atomic replacement primitive.
- Keep backups only through the canonical storage/backup facility and lifecycle;
  never leave ad hoc `.bak` files or alternate live sources.
- Define deletion and contradiction searches before implementation.

### 4. Implement owner-first

- Change typed models, schema validators, and generator inputs first.
- Update the official migration command in the owning project; do not create a
  one-off shell/Python rewrite outside the owner.
- Rewire every consumer and regenerate projections through the official command.
- Delete the old schema and all old code in the same change.
- Reject old-format input explicitly after cutover. Do not auto-detect or silently
  translate it at runtime.

### 5. Prove completeness

Run repository-native commands for:

- schema/model validation and invalid-old-format rejection;
- migration tests, including representative production-shaped data and a second
  idempotence run;
- generator apply followed by fixed-point check;
- lint, formatting, type checking, unit, integration, security, and build gates;
- runtime validation through every supported public entry point; and
- repository-wide and related-repository searches showing zero active references
  to the superseded contract.

Warnings, skipped mandatory consumers, stale generated files, undocumented manual
steps, and unexplained scanner findings are failures.

### 6. Publish and close

- Integrate the current integration base using the repository's required method;
  never force-push or discard concurrent work.
- Commit the complete cutover and publish its PR with impact, approval, migration,
  deletion, and decisive gate evidence.
- A change is not complete until the PR is published and every user is rewired.
  Repository closure rules may additionally require approval, merge, deployment,
  runtime soak, and tracker closure.
- Never report completion from a local diff, partial PR, green subset, or planned
  follow-up.

## Required tests

At minimum, test:

- the final schema accepts valid final-format configuration;
- the old format is rejected;
- missing/invalid values fail with actionable errors;
- transformation preserves all required information;
- a second migration run makes no change;
- generated output reaches a two-run fixed point;
- every registered consumer loads and behaves through its real entry point; and
- searches find no live old-format keys, symbols, examples, or instructions.
