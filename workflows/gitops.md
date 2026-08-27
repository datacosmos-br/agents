# Workflow: GitOps / Kubernetes Change

## Goal
Change cluster state declaratively via Git, validated by ArgoCD.

## Prerequisites
- [ ] Read-only analysis confirms root cause
- [ ] You understand the ArgoCD app hierarchy
- [ ] Mutation is NOT Phase-0 bootstrap or DR (those use scripts)

## Steps

### 1. Read-Only Analysis (Mandatory)
```bash
# Get ArgoCD app state
make status WHAT=argocd,app

# Check for errors
make diagnose WHAT=app

# Read live resource state (read-only)
kubectl get <resource> -n <namespace> -o yaml
# OR
make status WHAT=pods,events,logs

# Diff live vs desired
make sync WHAT=diff
```

### 2. Extract Root Cause
From ArgoCD output, identify:
- Validation error?
- Webhook denial?
- RBAC 403?
- Missing CRD?
- Resource quota?
- Image pull failure?
- Finalizer conflict?
- Values drift?

### 3. Fix Declaratively in Git
```bash
# Edit the source manifest/chart/values
# NOT: kubectl edit, kubectl patch, kubectl delete

# For Helm charts: edit values.yaml or templates/
# For raw manifests: edit the YAML file
# For selectors: edit selector definitions
```

### 4. Validate Locally
```bash
# Render charts locally
make template

# Check rendered output
make check WHAT=render-noop

# Validate YAML/schema
make check WHAT=schema,lint
```

### 5. Commit and Let ArgoCD Reconcile
```bash
git add -u
git commit -m "fix(cosmos): description

ArgoCD app: <app-name>
Root cause: <from step 2>
Validation: make check WHAT=render-noop,schema (pass)"

# If user authorizes push:
git push
```

### 6. Verify Sync
```bash
# Wait for ArgoCD to sync
make sync WHAT=app

# Check health
make status WHAT=health

# Validate no drift
make sync WHAT=diff
```

## Forbidden Operations
- `kubectl edit` — never mutate live resources
- `kubectl patch` — fix source, not live state
- `kubectl delete` to force recreation — fix finalizers in source
- Manual `vault write` — update Vault chart/values
- `argocd app set` to bypass drift — fix in Git
- `argocd app sync --force` without understanding why force is needed

## Emergency Exception
If production is down and GitOps sync is blocked:
1. Document the exact manual command and output
2. Apply manual fix to restore service
3. Immediately update Git source to match
4. Verify ArgoCD will not revert the fix
5. Create incident bead tracking the bypass
