# Workflow: New Feature

## Goal
Implement a new feature with planning, incremental delivery, and full validation.

## Prerequisites
- [ ] Feature is scoped (not a vague idea)
- [ ] You are on a feature branch
- [ ] Project detected (see WORKFLOWS.md)

## Steps

### 1. Planning (Mandatory)
```bash
# Check existing architecture / patterns
cat AGENTS.md  # Project-specific rules
cat CLAUDE.md  # If exists

# Check beads for related work
bd list --all | rg -i "feature_name"

# Create plan bead (if using beads)
bd create "Feature: <name>" --type task --json
```

### 2. Spike / Explore (Optional)
```bash
# Read relevant code paths
# Use active structural tools: ast-grep, scope, or repository-native search
# Write a quick prototype to validate approach
# Discard prototype after learning
```

### 3. Implement Incrementally
- Start with interface / API definition
- Implement core logic
- Add tests alongside code (TDD preferred)
- Run validation after every significant edit:

```bash
# ── FLEXT ──
make check WHAT=fmt,types,lint && make test

# ── MCB ──
make check WHAT=fmt,lint,validate && make test

# ── cosmos-main ──
make check WHAT=quick,validate,scripts
```

### 4. Cross-Project Validation (FLEXT only)
```bash
# If the change affects multiple subprojects
make check WHAT=workspace
make test
```

### 5. Documentation
```bash
# Update docs if user-facing behavior changed
# FLEXT: update docstrings + README
# MCB: update rustdoc + mdBook
# cosmos-main: update ADR if architectural

make docs WHAT=validate
```

### 6. Final Validation
```bash
# ── FLEXT ──
make check WHAT=all && make test && make val

# ── MCB ──
make check WHAT=all && make test

# ── cosmos-main ──
make check WHAT=deep
```

### 7. Session End
```bash
git diff --stat
# If user authorizes:
git add -u
git commit -m "feat(scope): description

Implementation: <brief summary>
Validation: make check && make test && make val (all pass)"
```

## Decision Tree

```
Is the feature well-scoped?
├── NO  → Ask user to clarify: what exactly should change? What is out of scope?
│
└── YES → Does it touch multiple projects?
          ├── YES → Create beads for each, implement in dependency order
          │
          └── NO  → Does it need ADR / design doc?
                    ├── YES → Write ADR first, get user approval
                    └── NO  → Implement incrementally with validation gates
```
