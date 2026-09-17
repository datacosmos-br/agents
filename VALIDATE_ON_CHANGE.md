# Universal Law — Mandato Operacional (operador, 2026-09-16, emendada)

## Regra 1 — Validate-On-Change
Ao criar ou alterar QUALQUER coisa — código, chart, valores, lockfile, gitlink,
configuração, documentação — VALIDAR se está certo e funciona, imediatamente,
antes de seguir adiante.

### O que vale FUNDAMENTALMENTE
**O PLENO FUNCIONAMENTO EM RUNTIME.**
- Testes simples e evidências estáticas NÃO comprovam entrega — são, no máximo,
  sinais de apoio. Nunca substituem o runtime.
- Prova válida = o artefato/executável REAL operando de ponta a ponta no
  ambiente alvo: processo rodando, endpoint respondendo, render aplicado,
  fleet sincronizada e saudável, job concluído, dado fluindo.
- "Está certo" = adere aos contratos e padrões (SSOT, DRY, YAGNI, DI, FLEXT,
  PEP, Pydantic, semver strict — zero fallback/legacy/compatibilidade).
- "Funciona" = comportamento observado no runtime real, com output decisivo.
- Testes fora dos padrões de qualidade: remover. Testes testam realidade via
  interfaces públicas; o resto é descartável — e nunca anulam a prova runtime.

## Regra 2 — Sem pressa; status, beads e wip sempre atualizados
- Nunca fazer algo com pressa para concluir.
- Sempre atualizar os status e os beads à medida que o trabalho avança.
- Sempre gravar progresso como **wip local E remotamente** — via **worktree e
  branch dedicada de trabalho** — para que interrupções não percam estado.

## Regra 3 — Ciclo completo ou nada
- Se o ciclo completo não for feito — levar o trabalho até a **branch de
  integração** e, quando solicitado, até o **runtime** — o trabalho NÃO foi
  feito: é trabalho perdido.
- Entrega = PR/ciclo integrado na branch de integração + (quando pedido)
  validação viva no runtime. Estados intermediários são wip, não entrega.

## Regra 4 — NUNCA deduzir; pesquisar, entender, perguntar
**NUNCA, NUNCA, NUNCA tente deduzir. SEMPRE pesquise, entenda e, se houver
dúvidas, PARE E PERGUNTE. Nunca tente adivinhar ou deduzir.**
- Antes de qualquer comando/caminho/nome/API: descobrir o valor REAL na fonte
  (kubectl get, make help, docs, código) — nunca inventar.
- Dúvida ≠ decisão: dúvida = pergunta ao operador ou pesquisa funda até
  certificação. Ambiguidade resolvida por adivinhação é falta gravíssima.

## Regra 5 — Execução do plano (mandato de coordenação única)
- Executar o plano aprovado: P0 = reorganizar beads, épicos, tasks, docs, ADRs;
  depois as demais fases.
- Lane única em cosmos-main: ASSUMIR tudo — adotar, agrupar, reaproveitar
  (lanes, branches, PRs, wips) ou descartar dentro do plano.
- Resultado: projeto 100% funcional e completo com as funcionalidades acordadas.
- Green/green o tempo todo — local E CI — gravando na branch de integração a
  cada ponto green 100%, e aplicando em runtime sem demora.
- Máximo de subagentes (explorar/executar/validar/testar); coordenador fica com
  coordenação, aprovação, QA final e publicação.
- Corrigir ruff, mypy, pyright, pyrefly com tipagem strict.
- Helpers, models, protocols, typings, constants namespaced de u/m/p/t/c,
  declarados no dono, consumidos DRY. Lazy imports via __init__ preferidos
  (desempenho + ciclos); erros de import cíclico = violação das regras flext.
- Sync periódico com a branch de integração via merge --no-ff.
- Jeito mais novo e melhorado SEMPRE: zero fallback/legacy/compatibilidade —
  exterminar, rewired, revalidado no cluster dc-dese funcionando na real.
  Fix-forward adopt, nunca fallback/rollback.
- SSOT, YAGNI, DRY, DI, FLEXT, PEP, Pydantic: obrigatórios e strict.
- Resolver conflitos de PR/worktrees/branches/subprojetos: land de todos com
  cuidado, pegando as funcionalidades mais novas; ao final push PR, merge
  --no-ff com a integração, push, fecha PR, apaga worktrees/branches/PRs
  merged e fecha beads — fechando os ciclos.
- Automação máxima: ast-grep search/replace, make mod, crg, lsp refactor;
  testmon obrigatório (nunca full-suite fora do cache); APPLY=Y é a única
  flag de mutação; nada de seletores inventados no Make.
- Qualidade total: nenhum warning/erro/indireta mal configurada fica para
  depois; nada pendente; artefatos manual-list (ex.: class-nesting-mappings.yml)
  proibidos — descoberta automatizada pelas funções SSOT.
- Experiência ganha vira melhoria imediata de skills, commands, rules, docs e
  ADRs — sempre pelos ciclos.

## Non-negotiables adicionais (operador 16/09)
- exclude-newer, mise.lock e uv.lock: BANIDOS. Lockfiles nunca rastreados
  (fleet standalone contract); exclude-newer nunca injetado à mão — o gerador
  emite apenas exclude-newer-package a partir do toolchain SSOT. Qualquer
  reaparição é exterminada na hora, na origem.
- Mudança de regra/estratégia documentada ou em código, sem autorização ou
  ordem do operador, é falta gravíssima. Use a regra mais nova; se não der
  para determinar, pesquise a fundo a hierarquia e, persistindo a dúvida,
  PARE E PERGUNTE.

## Lições operacionais (2026-09-16, ciclo rope-modernize — operador emendando)
- **Branches/stashes/PRs antigos = análise de contribuição real**: o que contêm
  que o código atual e suas beads ainda não têm — adotar seletivamente só o
  unique delta útil. NUNCA diff-merge completo (traz stale/cerimônia; provado:
  dois merges de lanes aposentadas renderam tree idêntica, contribuição zero).
- **Probe nunca vai no commit**: antes de cada commit, grep no staged por
  `environ.get|print(|FLEXT_DEBUG` — probe é env-gated, in-file, revertido.
- **Evidência numérica = conjunto de test-ids F/E + exit code**; totals de
  "passed" com testmon selecionando não provam nada. Provar fix = re-run
  explícito do arquivo de teste owner.
- **Beads via direnv**: `eval "$(direnv export bash)"` antes de bd; endpoint
  dolt é city-owned (gascity) — nunca pinar porta, nunca `bd dolt set`,
  nunca fallback. `.beads/*` de membros: só as entradas permitidas pelo gate
  (config.yaml, metadata.json, .local_version, last-touched); resíduo runtime
  já-durável no dolt é lixo e se limpa.
- **Loops de frota em script-arquivo** (~/tmp/kilo/*.sh) rodando em background
  com análise de log — nunca loops inline `bash -c` (expansão de variável
  dentro de aspas já quebrou uma varredura inteira). Subagentes para análise
  de logs grandes.
- **Dirty idêntico em N membros = drift de projeção** do template absorvido:
  adotar (preserve-commit scoped) + merge; provar por amostragem (1 repo via
  `git diff HEAD...origin/<integ>`), não investigar por repo.

Precedence per `rules/coordination/operator-precedence.md`.
