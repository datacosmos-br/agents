# Atomic configuration-schema migration

## Approval and impact

Before changing a public contract, present the exact old and proposed schemas,
affected consumers, persisted-data transformation, breaking behavior, and
deletion plan for operator approval. Internal changes may proceed only when the
repository proves they are not externally observable.

Inventory the typed schema owner, generators, writers, stored instances,
loaders, validators, runtime consumers, commands, tests, examples, and documents.
If every scoped consumer cannot move in the same change, stop before introducing
a second live contract.

## Cutover

1. Define one final schema and a deterministic transformation.
2. Make the transformation fail loudly on ambiguous or invalid input and make a
   second run on final-format input produce no change.
3. Change the typed owner and official migration surface.
4. Transform persisted data with the repository's atomic storage primitive.
5. Rewire every producer and consumer and regenerate managed outputs.
6. Delete old fields, loaders, writers, fixtures, examples, documentation, and
   terminology. Final runtime readers explicitly reject old-format input.

Do not add aliases for removed fields, fallback readers, dual writes, feature
flags, deprecation windows, hardcoded translations, or ad hoc backup files.

## Proof

Run the final-format runtime through every supported public entry point before
adjusting tests. Then prove valid final input, invalid and old input rejection,
information preservation, a second no-op migration, generated fixed point, and
the repository's static, behavioral, security, and build gates. Search the
scoped source tree for every removed key and term; any live match blocks closure.
