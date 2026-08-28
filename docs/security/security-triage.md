# Triagem de segurança — agents

Este arquivo registra decisões técnicas e a evidência reproduzível mais recente;
não é tracker nem prova de que um commit futuro está verde. O SHA que será
publicado exige nova execução de `make security`, com comando, diretório, exit
code e output decisivo no PR/CI. A decisão técnica de um finding não fecha a
fase: enquanto o tracker canônico estiver suspenso, nenhuma fase pode ser
declarada DONE. Durante a suspensão, o estado permanece no ledger manual
canônico do repositório.

## Findings

### 1 · HIGH · GitHub Actions checkout mutable

**Decisão**: corrigido no owner do workflow; revalidação obrigatória no SHA final

**Evidência**: em `/home/marlonsc/.agents`, Semgrep 1.174.0 executado pelo alvo
`make security` retornou código 0, 607 regras, 1001 alvos e zero findings; o
inventário `rg '^\s*-?\s*uses:' .github/workflows` mostra `actions/checkout`
fixado por SHA completo.

### 2 · HIGH · GitHub Actions setup-uv mutable

**Decisão**: corrigido no owner do workflow; revalidação obrigatória no SHA final

**Evidência**: em `/home/marlonsc/.agents`, Semgrep 1.174.0 executado pelo alvo
`make security` retornou código 0, 607 regras, 1001 alvos e zero findings; o
inventário `rg '^\s*-?\s*uses:' .github/workflows` mostra `astral-sh/setup-uv`
fixado por SHA completo.

### 3 · HIGH · GitHub Actions upload-artifact mutable

**Decisão**: corrigido por remoção do consumidor; revalidação obrigatória no SHA final

**Evidência**: em `/home/marlonsc/.agents`, Semgrep 1.174.0 executado pelo alvo
`make security` retornou código 0, 607 regras, 1001 alvos e zero findings; o
inventário completo de `uses:` em `.github/workflows` não contém
`actions/upload-artifact` e contém somente referências por SHA completo.

### 4 · MEDIUM · Permissões de scratch

**Decisão**: corrigido no owner de scratch; revalidação obrigatória no SHA final

**Evidência**: `uv run pytest -q tests/test_temp.py` retornou código 0 com 24
testes; `temp.py` cria o owner e os subdiretórios com modo `0700`; Semgrep
1.174.0 retornou código 0 e zero findings, sem nova suppression.

### 5 · LOW · Dependências e segredos

**Decisão**: corrigido; revalidação obrigatória no SHA final

**Evidência**: em `/home/marlonsc/.agents`, Gitleaks 8.30.1 retornou código 0 e
`no leaks found`; Snyk 1.1306.4 testou 16 dependências com código 0, zero issues
e zero vulnerable paths. Ambos foram executados pelo alvo owner `make security`;
o commit candidato exige uma nova execução integral.
