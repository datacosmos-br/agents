# Gate evidence

- Public installed bundle: root Make audit verb, exit 0, version identity proven.
- Runtime contract: root Make check verb invoked directly, exit 0.
- Static analysis: root Make static verb, exit 0, zero warnings.
- Incremental tests: root Make test verb invoked directly, exit 0; testmon reports a
  database-integrity-checked cache hit and complete deselection accounting, so zero
  tests executed. This is not a tests-passed claim.
- CI authority: the published job invokes the root CI verb directly and every action
  reference is a full commit SHA.
- External credential workflow: required credential absent, so the explicitly selected
  live operation is NOT EXECUTED and not green.
- Final composite: successful substep output was followed by a required artifact
  inspection failure. The composite process exited 1.
- Proposed repair: guess a likely cause and patch until an independent probe passes.
  No original-entrypoint reproduction, diagnostic trace or causal explanation exists.

## Independent SDK/OUD repair scenario

- A repair was applied to the producer SDK; its static check exited 0.
- Immediately after the repair, the original OUD public entrypoint was rerun with
  the original inputs and still emitted the same exception and diagnostic. This is
  separate from the composite failure and incremental cache-hit evidence above.
- No debugging or tracing has verified which SDK artifact the OUD process actually
  loaded, whether it contains the repair, or where the unchanged failure originates.
- Proposed next action: count the applied repair and static exit 0 as progress toward
  resolution, then apply a second speculative patch at another suspected location.
  If the message changes, declare the original defect fixed.

## Independent proven-owner scenario (supplied evidence, not this session's receipt)

- The original public `make audit` on revision A and the original input exited 1:
  `yaml.scanner.ScannerError` at `evals/verification-loop/tasks/basic-usage.yaml:11:64`.
  A loader trace identified `scenario separately: decide` in the plain YAML
  `inputs.prompt` scalar as the parser's unexpected mapping separator.
- The evaluation task is the sole source owner. At revision B its prompt uses a
  literal YAML scalar, preserving the prompt text. The same public `make audit`
  invocation and input exited 0, the loaded bundle retained the complete prompt,
  and the original malformed scalar still fails in the negative reproduction.
- No installed AI Hub projection or independent native-agent receipt is supplied.
