# Python debugging

## Evidence first

Capture expected behavior, observed behavior, the smallest reproducible input,
the exact exception or log, and the relevant Python and dependency versions.
Separate confirmed working, failing, and untested surfaces.

Build falsifiable hypotheses around boundaries, state mutation, concurrency,
configuration, integration contracts, and input edge cases. For each hypothesis,
record the evidence that would confirm or reject it. Trace the causal chain from
the earliest incorrect state to the visible symptom.

## Correction

Change the owning implementation, not the symptom or the test expectation.
Preserve the original exception when translation is unnecessary. Add a
regression test that reproduces the old failure through an observable public
surface, including the boundary condition that triggered it.

Report the confirmed cause, eliminated hypotheses, changed owner, runtime proof,
and focused gates. An incomplete reproduction is a blocker to a confident fix,
not permission to guess.
