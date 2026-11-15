# Applying a rule catalog

Procedure for running a repository's existing rules through its declared verb
(`make mod` in FLEXT). Authoring a rule is [authoring](authoring.md).

## Triage first

Run the engine once in inspection mode with no selection and read its findings
report. Sort the rules into three groups and state each group's count:

- actionable: the engine holds a rewrite and reaches a fixed point;
- detection only: the rule has no rewrite;
- actionable but not converging: the rewrite leaves its own findings behind.

The counts decide the plan; nothing is applied before they are known.

## Order

1. Repository blockers. A cyclic import, an inverted layer, a module named
   differently from the class it holds, or a local name that shadows a facade
   letter stops the engine before any rule applies. Each is fixed at its cause
   in its own change.
2. Actionable rules, as groups of companions: a normalizing rule runs together
   with the import and annotation rules it depends on, selected by law where
   the catalog declares one. A rule that normalizes never runs alone, and the
   whole catalog never runs in one command.
3. Detection-only rules with a mechanical correction. The code is reorganized
   so the rule no longer matches, or the missing rewrite is requested from the
   engine's owner with the measured case.
4. Detection-only rules that need authorship. Done by domain, with review.

## After each application

- Regenerate the managed files, then run the complete suite through the
  catalog's test verb, not only the tests of the files that changed.
- A defect the engine introduced is repaired by hand, covered by a test and
  reported to the engine's owner with the reproducing case.
- One group lands as one small change through the integration branch before
  the next group starts.

Record the group, the verb, the counts before and after, and the suite result
on the change.
