# Workflow: Refactor

## Goal
Improve code quality without changing behavior. Net-negative LOC preferred.

## Prerequisites
- [ ] Tests exist and pass before refactoring
- [ ] You are on a feature/refactor branch
- [ ] Scope is limited (one module or pattern at a time)

## Steps

### 1. Baseline
```bash
# Ensure tests pass before touching anything
# FLEXT
make test

# MCB
make test

# Save test output as baseline
```

### 2. Analyze
```bash
# Identify target: duplication, complexity, or outdated patterns
# Use active structural tools:
# - ast-grep for structural patterns
# - scope for code maps, sketches, and call graphs
# - repository-native search for exact references

# Check complexity metrics
# MCB: cargo clippy -- -D warnings
# FLEXT: ruff check + pyrefly check
```

### 3. Refactor
- Apply one refactoring at a time
- Run tests after each change
- Use `/simplify` command if available (triggers 4-agent review)

### 4. Validate Behavior Preserved
```bash
# Tests must pass identically
# FLEXT
make check WHAT=fmt,types,lint && make test

# MCB
make check WHAT=fmt,lint,validate && make test

# Compare test count with baseline
# Must be same or higher (new tests for edge cases discovered)
```

### 5. Validate Quality Improved
```bash
# Check net LOC change
git diff --stat
# Should be net-negative or neutral for pure refactor

# Check complexity reduced
# MCB: re-run clippy
# FLEXT: re-run ruff + pyrefly
```

### 6. Session End
```bash
git diff --stat
git add -u
git commit -m "refactor(scope): description

Before: <what was wrong>
After: <what improved>
LOC: <+X -Y>
Validation: make check && make test (all pass)"
```

## Forbidden Refactors
- Never refactor without passing tests first
- Never refactor and add features in the same commit
- Never refactor across module boundaries without updating beads
