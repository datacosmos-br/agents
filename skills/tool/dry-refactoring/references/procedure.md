# dry-refactoring — baseline and extraction procedure

## Comparison boundary

Use eight lines and strict mode unless the selected project explicitly owns a
different floor. Resolve the project gate before ad-hoc flags; an existing
baseline is valid only with its exact threshold, mode, formats, ignores, and
reviewed file set. Changing any of them invalidates prior green output and
requires triage before a new baseline.

For cross-repository work, materialize committed integration refs into a
worktree sibling snapshot on the destination filesystem. Archive each recorded
submodule commit from its own object database. Never substitute dirty checkout
state, another branch, `/tmp`, or a local default. Report the exact ref or
commit used for every snapshot.

## Triage

Classify every reported pair before editing:

- **semantic** — same behavior, contract, error policy, and current consumers;
  extract at the existing canonical owner;
- **canonical projection** — edit or regenerate the writable owner; never patch
  a generated copy;
- **historical/generated** — preserve evidence and regenerate only through its
  owner;
- **distinct fixture** — tests may differ intentionally in setup, error, or
  invariant; do not merge them merely to satisfy the detector;
- **tokenizer false positive** — unrelated Markdown, YAML, configuration, or
  prose shape.

A rebaselined entry must belong to one of the last four reviewed classes. A new
baseline is an atomic review artifact, never a suppression mechanism. If triage
is incomplete, fail closed with zero edits and no baseline replacement.

**Extract function** — the duplicate is a block of logic: move it to one
shared function called from both sites.

**Extract module/utility** — the duplicate spans files in different domains:
move shared logic to a utility file and import it.

**Extract constant or config** — repeated data or configuration.

**Template/base class** — structural duplication (repeated class shape).

Always:

- update all call sites, not just the two jscpd reported;
- keep tests passing after the refactoring;
- give the extracted abstraction a clear, descriptive name.
- rerun with the exact comparison configuration and prove `new clones: 0`.
