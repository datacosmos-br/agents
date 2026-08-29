# Triagem de segurança — agents

Este arquivo registra decisões técnicas e a evidência reproduzível mais recente;
não é tracker nem prova de que um commit futuro está verde. O SHA que será
publicado exige nova execução de `make security`, com comando, diretório, exit
code e output decisivo no PR/CI. A decisão técnica de um finding não fecha a
fase: enquanto o tracker canônico estiver suspenso, nenhuma fase pode ser
declarada DONE. Durante a suspensão, nenhum tracker ou ledger substituto é
criado; evidência permanece apenas em Git/PR/CI quando autorizados.

Os *findings* abaixo são detecções de domínio produzidas por scanners, não
normalizações de falhas de execução. Um scanner nonzero, timeout, sinal ou
publicação incompleta encerra `agentsctl secure` com a exceção e causa brutas;
nenhum desses erros pode virar um finding, warning, skip ou resultado neutro.

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
o commit candidato exige uma nova execução integral. No ciclo de 2026-08-28, a
API do Dependabot identificou 34 alertas abertos nos manifests versionados das
fixtures. O owner foi corrigido para `@modelcontextprotocol/sdk` 1.30.0 e Next.js
16.3.2, ambos fora do cooldown mínimo de sete dias; instalações físicas
isoladas e `npm audit --audit-level=low` retornaram código 0 e zero
vulnerabilidades para os dois conjuntos. A automação `.github/dependabot.yml`
agora cobre `uv`, as duas fixtures npm e GitHub Actions com cooldown de sete
dias, e o contrato offline valida essa cobertura.

`SNYK_TOKEN` não existe no ambiente do processo atual. Portanto, Snyk está `NOT
EXECUTED` neste commit e não fornece evidência verde. Uma invocação indevida de
`make security` depois de a ausência já estar provada retornou código 2 com
`ValueError: required environment variable is missing or empty: SNYK_TOKEN`;
essa falha é registrada como incidente, não como execução válida do scanner. O
comando `security-triage`, as skills `security-review` e `sprint-closure` e suas
regressões foram corrigidos para proibir nova seleção nessa condição e impedir
fechamento enquanto findings independentes permanecerem abertos.
