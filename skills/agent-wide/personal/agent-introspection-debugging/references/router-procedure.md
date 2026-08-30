# Agent Introspection Debugging — Procedure

Use this skill when an agent run is failing repeatedly, consuming tokens without progress, looping on the same tools, or drifting away from the intended task.

This is a workflow skill, not a hidden runtime. It teaches the agent to debug itself systematically before escalating to a human.

## When to Activate

- Maximum tool call / loop-limit failures
- Repeated attempts with no forward progress
- Context growth or prompt drift that starts degrading output quality
- File-system or environment state mismatch between expectation and reality
- Tool failures that require a read-only discriminating check before any correction

## Scope Boundaries

Activate this skill for:

- capturing the first causal failure before taking another action
- diagnosing common agent-specific failure patterns
- applying contained recovery actions
- producing a structured human-readable debug report

Do not use this skill as the primary source for:

- feature verification after code changes; use `verification-loop`
- framework-specific debugging when a narrower technology skill already exists
- runtime promises the current harness cannot enforce automatically

## Four-Phase Loop

### Phase 1: Failure Capture

Before trying to recover, record the failure precisely.

Capture:

- error type, message, and stack trace when available
- last meaningful tool call sequence
- what the agent was trying to do
- current context pressure: repeated prompts, oversized pasted logs, duplicated plans, or runaway notes
- current environment assumptions: cwd, branch, relevant service state, expected files

Minimum capture template:

```markdown
## Failure Capture
- Session / task:
- Goal in progress:
- Error:
- Last successful step:
- Last failed tool / command:
- Repeated pattern seen:
- Environment assumptions to verify:
```

### Phase 2: Root-Cause Diagnosis

Match the failure to a known pattern before changing anything.

| Pattern | Likely Cause | Check |
| --- | --- | --- |
| Maximum tool calls / repeated same command | loop or no-exit observer path | inspect the last N tool calls for repetition |
| Context overflow / degraded reasoning | unbounded notes, repeated plans, oversized logs | inspect recent context for duplication and low-signal bulk |
| `ECONNREFUSED` / timeout | selected service path failed | preserve the causal error and verify the configured endpoint read-only |
| `429` / quota exhaustion | selected external path is unavailable | preserve the response and stop without another request |
| file missing after write / stale diff | race, wrong cwd, or branch drift | re-check path, cwd, git status, and actual file existence |
| tests still failing after "fix" | wrong hypothesis | isolate the exact failing test and re-derive the bug |

Diagnosis questions:

- is this a logic failure, state failure, environment failure, or policy failure?
- did the agent lose the real objective and start optimizing the wrong subtask?
- what exact evidence distinguishes the leading hypothesis from the alternatives?
- what is the smallest reversible action that would validate the diagnosis?

For runaway shell, interpreter, loader, or agent processes, read the
`process-forensics procedure` (skill file) before containment.
It owns producer attribution, persistence discovery, and narrow process/file
boundaries.

### Phase 3: Contained Recovery

Run exactly one read-only check that discriminates the chosen hypothesis. If it
fails, preserve that causal failure and stop. If it succeeds, preflight the one
authorized correction completely before applying it.

Safe recovery actions:

- stop repeated attempts and restate the hypothesis
- trim low-signal context and keep only the active goal, blockers, and evidence
- re-check the actual filesystem / branch / process state
- narrow the task to one failing command, one file, or one test
- switch from speculative reasoning to direct observation
- escalate to a human when the failure is high-risk or externally blocked

Do not claim unsupported auto-healing actions like "reset agent state" or "update harness config" unless you are actually doing them through real tools in the current environment.

Contained recovery checklist:

```markdown
## Recovery Action
- Diagnosis chosen:
- Smallest action taken:
- Why this is safe:
- What evidence would prove the fix worked:
```

### Phase 4: Introspection Report

End with a report that makes the recovery legible to the next agent or human.

```markdown
## Agent Self-Debug Report
- Session / task:
- Failure:
- Root cause:
- Recovery action:
- Result: success | blocked
- Token / time burn risk:
- Preventive follow-up after the current failure is resolved:
- Preventive change to encode later:
```

## Recovery Heuristics

Prefer these interventions in order:

1. Restate the real objective in one sentence.
2. Verify the world state instead of trusting memory.
3. Shrink the failing scope.
4. Run one discriminating check.
5. Only then apply the single authorized correction.

Bad pattern:

- repeating the same failed action with slightly different wording

Good pattern:

- capture failure
- classify the pattern
- run one direct check
- change the plan only if the check supports it

## Integration

- Use `verification-loop` after recovery if code was changed.
- Record a durable preventive change only after the current failure and every
  attributable effect are resolved through the active project's declared owner.

## Output Standard

When this skill is active, do not end with "I fixed it" alone.

Always provide:

- the failure pattern
- the root-cause hypothesis
- the recovery action
- the evidence that the situation is now better or still blocked
