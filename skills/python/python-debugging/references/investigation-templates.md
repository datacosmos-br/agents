# Investigation templates (python-debugging)

## Intake checklist

```text
SPEC: expected behavior? acceptance criteria?
OBSERVED: actual behavior? exact errors? relevant logs?
REPRO: steps? triggering input? env (Python/OS/deps)?
CONTEXT: last known good? recent changes? intermittent or consistent?
```

## Scope boundaries

```text
WORKING: [features confirmed ok]
NOT WORKING: [features failing, how]
UNKNOWN: [untested surface]
Questions: regression or never worked? all inputs or specific? all envs or specific? smallest repro?
```

## Hypothesis register

```text
H<n>: <potential cause>
  evidence for / against:
  test to verify:
```

Common categories: type error (check boundary types) · state mutation (shared mutable state) · race (async/threading) · edge case (boundary inputs) · integration (interface contracts) · configuration (env delta).

## Root-cause report

```text
Confirmed cause: <desc>
Evidence: [file:line] / [log] / [test result] — what each shows
Causal chain: root cause -> symptom
Eliminated: H2 because ..., H3 because ...
Fix spec: location, approach, risks, tests (regression + edges)
```

## Regression test pattern

```python
def test_<bug>_regression():
    input_data = create_problematic_input()   # arrange: triggers the bug
    result = fixed_function(input_data)       # act
    assert result == expected_output          # assert: old failure gone
    assert result.specific_field == expected_value
```
