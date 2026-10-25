# Runtime-first behavioral regression

## Contract

The approved public contract and measured real execution define the target. Tests
validate implemented functionality; they neither invent behavior nor precede its
implementation. Compose `engineering-core`, `runtime-is-reality` and
`observable-runtime` for their mandatory ordering and evidence contracts.

## Procedure

1. Read project law, the public surface, affected consumers and their documented
   contract. Reconcile affected documentation and selected tracker records through
   their canonical owners before implementation. Resolve the native runtime and
   validation commands without guessing them.
2. Observe the defect through the real public entrypoint, not a newly written test.
   Preserve its command, source identity, effects and first causal failure. An
   observation of the old defect does not authorize editing tests yet.
3. Correct the canonical owner with the smallest complete implementation. Rewire
   affected consumers and remove the superseded path. Add no mock, fallback,
   alternate implementation, copied policy value or test-only production hook.
4. Exercise the corrected real public runtime and affected consumers. Prove outputs,
   errors, ordering and durable effects against the approved contract. A missing
   prerequisite or native failure remains unresolved; never claim success from a
   plan, command description or test expectation.
5. Only after that proof, correct the applicable static findings while keeping real
   execution working. Preserve unexpected nonzero exits, warnings, timeouts,
   signals and native causal chains; no retry or alternate validation path.
6. At the final validation stage, create or adjust regression coverage through public
   interfaces and existing typed fixtures. Use independent behavioral expectations,
   not answers computed by the implementation or tautological receipt checks.
7. Run the declared focused tests and applicable integration/full validation. Every
   Python test invocation follows the verbs and testmon contract owned by
   `rules/workflow/canonical-commands.md`. A failure returns work to its causal
   owner without weakening assertions or restoring the removed behavior.

## Test selection

- Unit tests cover pure behavior and boundary conditions.
- Integration tests cover real component contracts and persistence boundaries.
- End-to-end tests cover critical user or operator journeys through the public surface.
- Do not use mocks, monkeypatching, patched construction, or private imports. Provision
  a real boundary through the project-owned typed fixture and exercise its public
  contract.
- In `internal_flext`, reuse `flext-tests` public `tm`, `c`, `t`, `p`, `m`, and `u`
  facets plus the shared conftest; never copy that machinery locally.
- Coverage reports reveal missing paths; an arbitrary percentage is not proof of
  correctness.

## Completion

Report the original defect observation, corrected runtime command and artifact,
independent regression oracle, native validation receipts, affected consumers,
first causal failure, zero-effect proof, residue search and remaining blocker.
Never claim completion from a test name, test count, proposed command or coverage
percentage alone.
