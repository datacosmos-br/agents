# Workflow: Bug Fix

## Goal
Fix a bug with root-cause analysis, minimal change, and full validation.

## Prerequisites
- [ ] `git status` shows clean working tree or known state
- [ ] You are on the correct branch (feature/fix branch, not main)
- [ ] Project detected (see WORKFLOWS.md)

## Steps

### 1. Understand the Bug (Investigate)
```bash
# Read error logs, stack traces, or user description
# Search codebase for related code
grep -rn "error_pattern" src/ tests/
# Or use active structural tools: ast-grep, scope, or repository-native search
```

### 2. Reproduce
```bash
# FLEXT: run specific failing test
pytest tests/path/to/test_file.py::test_name -xvs

# MCB: run specific failing test
cargo test --package mcb-domain test_name -- --nocapture

# cosmos-main: check live state (read-only)
make status WHAT=app,health
```

### 3. Root Cause Analysis
```bash
# Use scientific method — form hypothesis, test, validate
# Search for related tests to understand expected behavior
grep -rn "related_function" tests/
# Check git history for recent changes
git log --oneline -10 -- path/to/file
```

### 4. Implement Fix
- Make the **smallest possible change** that fixes the bug
- Add or update tests that reproduce the bug
- Follow project typing and lint rules

### 5. Validate
```bash
# ── FLEXT ──
make check WHAT=fmt,types,lint && make test

# ── MCB ──
make check WHAT=fmt,lint,validate && make test

# ── cosmos-main ──
make check WHAT=quick,validate,scripts
# If K8s manifests changed:
make check WHAT=render-noop
```

### 6. Evidence Collection
```bash
# Show what changed
git diff --stat
git diff path/to/fixed_file

# Show tests passing
# (output from step 5)
```

### 7. Session End
```bash
# Update beads tracking
bd update <id> --json

# If user authorizes:
git add -u
git commit -m "fix(scope): description

Root cause: <one-line explanation>
Validation: make check && make test (all pass)"
```

## Decision Tree

```
Can you reproduce the bug?
├── NO  → Ask user for more info / logs / environment
│
├── YES → Is the root cause clear?
│         ├── NO  → Add debug logging / tracing, reproduce again
│         │
│         └── YES → Is the fix a one-liner?
│                   ├── YES → Fix + test + validate + done
│                   │
│                   └── NO  → Does it need a design change?
│                             ├── YES → Escalate to feature workflow
│                             └── NO  → Fix + test + validate + done
```
