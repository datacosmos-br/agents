# Workflow: Documentation

## Goal
Update or create documentation that matches the current code state.

## Prerequisites
- [ ] The code change that requires docs is already implemented and validated
- [ ] You know the audience (user docs, API docs, ADR, runbook)

## Steps

### 1. Identify What Needs Docs
```bash
# Check for stale docs
git diff --name-only | grep -E '\.(md|rst)$'
# Check for undocumented public APIs
# MCB: cargo doc --document-private-items 2>&1 | grep "missing_docs"
# FLEXT: check docstring coverage
```

### 2. Write / Update
- Update docstrings/comments for code changes
- Update user-facing docs (README, guides)
- Update ADR if architectural decision changed
- Update runbooks if operational behavior changed

### 3. Validate Docs
```bash
# ── FLEXT ──
make docs WHAT=validate
make check WHAT=markdown

# ── MCB ──
make docs WHAT=lint,validate
# Check rustdoc builds without warnings
cargo doc --no-deps 2>&1 | grep -i "warning" || true

# ── cosmos-main ──
make docs WHAT=validate,standardize
make check WHAT=adr
```

### 4. Cross-Reference Check
```bash
# Ensure all links work
# Ensure code examples in docs compile/run
# Ensure ADR index is up to date
```

### 5. Session End
```bash
git add -u
git commit -m "docs(scope): description

Changes: <what docs changed>
Validation: make docs (pass)"
```

## Rule
Docs must be updated in the **same bead** as the code change that makes them necessary. Stale docs become bug beads.
