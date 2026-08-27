# Triagem de segurança — agents

Ledger: manual

## Findings

### 1 · HIGH · GitHub Actions checkout mutable

**Decisão**: corrigido

**Evidência**: `semgrep scan --config p/default --error --metrics=off .` retornou zero findings após pin por SHA completo.

### 2 · HIGH · GitHub Actions setup-uv mutable

**Decisão**: corrigido

**Evidência**: `semgrep scan --config p/default --error --metrics=off .` retornou zero findings após pin por SHA completo.

### 3 · HIGH · GitHub Actions upload-artifact mutable

**Decisão**: corrigido

**Evidência**: `semgrep scan --config p/default --error --metrics=off .` retornou zero findings após pin por SHA completo.

### 4 · MEDIUM · Permissões de scratch

**Decisão**: corrigido

**Evidência**: diretórios são criados diretamente com modo `0700`; a nova execução Semgrep retornou zero findings sem suppression.

### 5 · LOW · Dependências e segredos

**Decisão**: corrigido

**Evidência**: `snyk test --all-projects --exclude=.venv,.cache,.test-tmp --severity-threshold=low` e `gitleaks detect --no-banner --source . --exit-code 1 --redact` retornaram zero issues.
