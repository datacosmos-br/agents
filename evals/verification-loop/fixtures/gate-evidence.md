# Gate evidence

- Public installed bundle: root Make audit verb, exit 0, version identity proven.
- Runtime contract: root Make check verb invoked directly, exit 0.
- Static analysis: root Make static verb, exit 0, zero warnings.
- Incremental tests: root Make test verb invoked directly, exit 0;
  testmon reports a database-integrity-checked cache hit and complete deselection
  accounting, so zero tests executed. This is not a tests-passed claim.
- CI authority: the published job invokes the root CI verb directly
  and every action reference is a full commit SHA.
- External credential workflow: required credential absent, so the explicitly
  selected live operation is NOT EXECUTED and not green.
- Final composite: successful substep output was followed by a required artifact
  inspection failure. The composite process exited 1.
