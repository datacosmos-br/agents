# Fail-fast extermination procedure

## Critical runtime prohibition

Treat every confirmed silent-failure or automatic-failover path as a critical,
release-blocking runtime defect. It can report a failed mutation as committed,
serve stale or partial output, corrupt durable state, lose or duplicate work,
leave processes consuming resources after cancellation, conceal a security
failure, or redirect execution to the wrong model, provider, endpoint,
credential, implementation, or database.

Never accept, defer, suppress, downgrade, document around, or retain such a
path. The only resolution is root-cause correction plus loud propagation and
fresh runtime proof. A lexical match that semantic tracing proves non-error
behavior is not a confirmed path.

## Establish the contract

Identify the operation owner, the requested success invariant, every observable
failure signal, and the caller responsible for handling it. Success requires a
fresh result produced by the current invocation. A warning, log line, cached
artifact, empty value, skipped check, or child process still running is not
success.

Automatic failover is prohibited. On failure, do not select another model,
provider, endpoint, database, implementation, credential source, or cached
result. Preserve the original cause and stop at the nearest boundary that can
add useful context.

## Loud-propagation law

A failure remains an error until exactly one valid terminal action occurs:

1. the owning implementation corrects the root cause and fresh runtime proves
   the original operation succeeds;
2. a CLI or process boundary catches the typed failure only to add actionable
   context, writes it to `stderr`, and returns a documented nonzero exit; or
3. when neither correction nor an owning CLI boundary is available in the
   authorized scope, the agent reports the unresolved failure prominently in
   its final response as a warning or blocker with the exact command, exit code,
   decisive output, and required next owner action.

A log record, metric, retry, internal warning, neutral return, empty collection,
`None`, cached result, or successful exit does not handle an error. Catch only
to translate at an owning boundary or to add context and re-raise while
preserving the original cause. Cleanup errors must also propagate; when cleanup
and operation both fail, expose both without replacing the first cause.

## Inventory semantic failure sinks

Search producers, consumers, tests, scripts, CI, generated surfaces, and docs.
Trace behavior rather than treating syntax matches as findings. Inspect:

- empty or broad exception handlers, log-and-continue paths, and unobserved
  futures, tasks, callbacks, or process groups;
- catches that emit an internal warning but return success, and agent responses
  that omit or soften a command failure;
- ignored subprocess exit codes, `|| true`, unconditional zero exits, discarded
  stderr, optional scanners, and gates that validate nothing;
- neutral returns after an error, permissive parser defaults, missing required
  fields accepted as empty, and partial writes exposed as final artifacts;
- retries that erase the first cause, error-triggered rerouting, compatibility
  readers, alternate credentials, stale candidates, and cached success;
- timeouts or cancellation that leave owned work running, and cleanup failures
  that are suppressed;
- tests that assert only non-empty output, execution completion, or an old
  artifact without proving provenance and freshness.

For each candidate record the exact signal lost, the false-success outcome, the
owner boundary, the required observable error, and the test that will prove the
repair. During tracker suspension, record its bounded state in the
repository-declared manual ledger.

## Classify without false positives

A candidate is valid only when the operation's declared contract explicitly
defines the condition as nonfatal, the caller observes the typed result, no
failed invariant is reported as success, and focused tests prove both branches.
Collecting all independent validation errors before one nonzero exit is still
fail-fast because the command never publishes success. UI placeholders and
ordinary load balancing are not error-triggered failover.

If the source, owner, or success contract is missing, stop and request that exact
evidence. Never delete or rewrite a path based only on a lexical match.

## Replace at the owner

1. Write a failing test that injects the real failure at the owner boundary.
2. Remove the swallowed, alternate, or stale-success path completely.
3. Propagate a typed error while preserving the original cause. At the owning
   CLI boundary, render it to `stderr` and return a documented nonzero exit.
4. Add context without secrets; make the decisive error visible to every caller
   and, if it remains unresolved, to the user in the final response.
5. Produce artifacts in an invocation-unique candidate and promote atomically
   only after the producer and validator both succeed.
6. On interruption, terminate only the owned process group and prove no child
   remains.
7. Rewire every consumer and delete obsolete fallback tests, fixtures, docs,
   flags, aliases, and configuration. Do not keep old and new behavior together.

## Failure matrix

Exercise missing and malformed input, dependency absence, nonzero subprocess
exit, partial output, stale output, 401, 402, 403, 429, 5xx, timeout,
cancellation, concurrent execution, and cleanup failure where applicable. Each
case must prove:

- a nonzero or typed failure reaches the caller;
- the first causal error remains identifiable;
- no internal warning or log line replaces propagation;
- no alternate route runs;
- no stale or partial artifact is published;
- no owned child survives cancellation.

## Closure

Repeat semantic searches for the removed behavior, run the focused injected
failure matrix, then execute runtime, static, unit, integration, security, and
projection fixed-point gates. Report exact commands, exit codes, and decisive
output. Any unresolved failure is a prominent final-response warning or blocker,
never an omitted footnote or green claim. A phase remains open until its approved
PR is merged into the configured integration branch and its canonical tracker
item is closed.
