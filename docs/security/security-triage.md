# Triagem de segurança — agents

Este arquivo registra decisões técnicas e a evidência reproduzível mais recente;
não é tracker nem prova de que um commit futuro está verde. A aplicabilidade de
cada gate externo é resolvida antes da invocação. Um gate que exige token e não
o recebeu fica `NOT EXECUTED`, nunca verde; os gates offline e remotos aplicáveis
mantêm evidência própria. A decisão técnica de um finding não fecha a fase:
enquanto o tracker canônico estiver suspenso, nenhuma fase pode ser declarada
DONE. Durante a suspensão, nenhum tracker ou ledger substituto é criado;
evidência permanece apenas em Git/PR/CI quando autorizados.

Os *findings* abaixo são detecções de domínio produzidas por scanners, não
normalizações de falhas de execução. Um scanner nonzero, timeout, sinal ou
publicação incompleta encerra `agentsctl secure` com a exceção e causa brutas;
nenhum desses erros pode virar um finding, warning, skip ou resultado neutro.

## Findings

### 1 · HIGH · GitHub Actions checkout mutable

**Decisão**: corrigido no owner do workflow e revalidado no SHA publicado

**Evidência**: em `~/.agents`, Semgrep 1.174.0 executado pelo alvo
`make security` retornou código 0, 607 regras, 1001 alvos e zero findings; o
inventário `rg '^\s*-?\s*uses:' .github/workflows` mostra `actions/checkout`
fixado por SHA completo.

### 2 · HIGH · GitHub Actions setup-uv mutable

**Decisão**: corrigido no owner do workflow e revalidado no SHA publicado

**Evidência**: em `~/.agents`, Semgrep 1.174.0 executado pelo alvo
`make security` retornou código 0, 607 regras, 1001 alvos e zero findings; o
inventário `rg '^\s*-?\s*uses:' .github/workflows` mostra `astral-sh/setup-uv`
fixado por SHA completo.

### 3 · HIGH · GitHub Actions upload-artifact mutable

**Decisão**: corrigido por remoção do consumidor e revalidado no SHA publicado

**Evidência**: em `~/.agents`, Semgrep 1.174.0 executado pelo alvo
`make security` retornou código 0, 607 regras, 1001 alvos e zero findings; o
inventário completo de `uses:` em `.github/workflows` não contém
`actions/upload-artifact` e contém somente referências por SHA completo.

### 4 · MEDIUM · Permissões de scratch

**Decisão**: corrigido no owner de scratch e revalidado no SHA publicado

**Evidência**: `uv run pytest -q tests/test_temp.py` retornou código 0 com 24
testes; `temp.py` cria o owner e os subdiretórios com modo `0700`; Semgrep
1.174.0 retornou código 0 e zero findings, sem nova suppression.

### 5 · LOW · Dependências e segredos

**Decisão**: corrigido e revalidado no SHA publicado

**Evidência**: a API do Dependabot identificou inicialmente 34 alertas abertos
nos manifests versionados das fixtures. O owner foi corrigido para
`@modelcontextprotocol/sdk` 1.30.0 e Next.js 16.3.3; instalações físicas isoladas
e `npm audit --audit-level=low` retornaram código 0 e zero vulnerabilidades para
os dois conjuntos. A automação `.github/dependabot.yml` agora cobre `uv`, as duas
fixtures npm e GitHub Actions com cooldown de sete dias, e o contrato offline
valida essa cobertura.

Após o merge dos PRs 16, 17 e 18, `main` publicou o commit
`d8d7f26a00b1836b3e7eb9c0c4a49a91cec58116`. As duas execuções finais de `Run
Evaluations` e o scan Semgrep 218580766 terminaram em `SUCCESS`; a consulta
autenticada `GET /repos/marlon-costa-dc/agents/dependabot/alerts?state=open`
retornou zero alertas. Nenhum alerta foi dispensado ou suprimido.

`SNYK_TOKEN` não existe no ambiente do processo atual. Portanto, Snyk está `NOT
EXECUTED` neste ciclo e não fornece evidência verde. Uma invocação indevida de
`make security` depois de a ausência já estar provada retornou código 2 com
`ValueError: required environment variable is missing or empty: SNYK_TOKEN`;
essa falha é registrada como incidente, não como execução válida do scanner. O
comando `security-triage`, as skills `security-review` e `sprint-closure` e suas
regressões foram corrigidos para proibir nova seleção nessa condição e impedir
fechamento enquanto findings independentes permanecerem abertos.
