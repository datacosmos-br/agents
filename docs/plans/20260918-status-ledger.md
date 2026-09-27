# Status ledger — repo agents (2026-09-18, campanha dedicada)

> Auditoria plano-a-plano e bead-a-bead executada pela campanha dedicada de 18/09
> (mandato: agente único, fix-forward-adopt, colaboração com lanes paralelas por
> registro — nunca rollback). Método: leitura dos planos/ADRs + medição em runtime
> (gates via Make raiz, `bd` dentro do repo com direnv, git). Classificação de beads:
> **[A]** fechável/executável dentro do repo agents · **[M]** mista (parte agents +
> parte externa) · **[E]** externa (dono em outro repo — registrada, não executada
> aqui).

## 1. Veredito por plano/ADR

| Plano/ADR | Veredito | Evidência / ação |
| --- | --- | --- |
| kilo-distribution-gap-analysis | CUMPRIDO (header ABSORBED correto) | tasks 1/2/4/6 DONE por F2 (`56fcebdc`, `783b285c`); task 3 medida na ADR-0019; task 5 superseded. Resíduo `.kilo/` adjudicado na F3: `command/`+`agent/` (projeções aposentadas, contagens stale 121/12/64/56) removidos; `kilo.json` mantido (config da ferramenta do operador, não é catálogo) |
| reval250909-closure-plan | EXECUTADO (header retificado hoje) | PR #133 merge `ab27a954`; lanes aposentadas; F4 no runtime-program |
| governance-runtime-program (ag-zrh) | PARCIAL | F0/F2 ✓; F1 travada no lado ai-hub (ag-ey2k walker, 7 owner-fixes já em PR #737); ag-bwqu único bloqueador de código do piloto; F3 (ag-zrh.4) aguarda deploy |
| delivery-contract-behavioral-law (ag-p4a) | CUMPRIDO no repo | `c88cf7fd` (PR #135), release v0.5.0, ADRs 0017–0020; metade runtime (seção 5) é o elo ai-hub |
| pydantic-governance-plan | PARCIAL — lado agents completo | fases 0–3 + PR #127 ✓; resto é `flext-vjj1s.*` (DB flext); header atualizado hoje |
| ADR-0008 | CONTRADIÇÃO RESOLVIDA na F3 (`19e64c01`) | `cli.py`/`__main__.py` removidos; `projection.py` → `tools/governance_projection.py` (dev-only, fora do wheel); gen ponto-fixo ×2 + check + test-full 63 executados verdes |
| ADR-0014 intake | CUMPRIDO | `rules/workflow/capability-intake.md`; tríplice `flext-law` é defeito do consumidor (F5 do rework, dono ai-hub/flext) |
| ADR-0015 tag grammar v2 | CUMPRIDO no catálogo; parcial nas projeções | projeções versionadas (P5) entram na F4/F5 |
| ADR-0017/0018/0020/0021 | CUMPRIDOS | regras bootstrap presentes; v0.5.0; `advance.md` |
| ADR-0019 delivery contract | CUMPRIDO (o budget gate que bloqueou as gates era ele julgando correto) | causa-raiz real: reflow do prelude em `6978f43c`; fix `a1213d2c` |
| sync-alignment 18/09 | VIGENTE | 3 ações pendentes são dona ai-hub (seção 3 do handoff recuperado) |

## 2. Grafo de bloqueio (59 não-fechadas)

```
ag-nq7q ──blocks──> ag-q4w1 ──blocks──> ag-m9lu <──blocks── ag-bwqu
ag-ey2k ──blocks──> ag-zrh.2 ──blocks──> (F3 ag-zrh.4 / épico ag-zrh)
ag-2sc ──blocks──> ag-bak  (via ag-2sc.3 externo)
```

Cadeia crítica do piloto de homologação: `ag-bwqu` (acceptance real) + `ag-nq7q`
(CRG sync) + `ag-q4w1` (esteira make) → `ag-m9lu`. Todas as três raízes são [E] —
dono ai-hub; o piloto não destrava por trabalho catalog-side.

### Addendum 2026-09-20 (agents-dedicated, stabilization round — ver `20260920-stabilization-record.md`)

- Grafo atualizado: `ag-nq7q` **FECHADA** (CRG sync aplicado + gate
  `crg-check` permanente no Makefile via PR #157) → `ag-q4w1` destravada
  (aprovada e claimed). `ag-bwqu` **LANDED** no ai-hub (acceptance nativa,
  deploy.py consome `AiHubNativeDeploymentAcceptance`) + lei #814
  (credencial indisponível = NOT EXECUTED). `ag-ey2k` corrigida no ai-hub
  (`d1fb316be` +walker pointer) e evidência registrada. `ag-k89` FIX
  POUSADO (ai-hub PR #803: local-origin nunca vira external dependency;
  reconcile podou `gascity-build-141fc1`) + `ag-whr` fechada (isolamento
  provado). `ag-gmx` fechada (workflow dormente → épico flext-cpzjo).
- Grind de frota mapeado na lane `wip/stabilize-0.12-algar-20260919`
  (mypy 198→0, pyrefly 53→0 via cutover para donos tipados) e no
  worktree `wip/stabilize-0.12-root-20260919` (flext-infra commitado
  `020728af4`; imports circulares do merge corrigidos).
- Bloqueadores restantes do piloto: fix do `sync-crg-workspaces`
  (dedicado ai-hub, em diagnóstico) e o pouso flext com SHA (hold do
  make setup).

## 3. Beads [A] — fecháveis/executáveis no repo agents (plano de fechamento F6)

| ID | P | Ação | Evidência exigida/produzida |
| --- | --- | --- | --- |
| ag-aq8 | P0 | FECHAR (épico) | 7/7 filhos fechados; PR #131 + `ab27a954` |
| ag-vky | P0 | FECHAR | lei landed PR #84 (`5a56b124`, `rules/git/gitflow-branch-pr.md:53-59`) |
| ag-22s | P0 | VERIFICAR→FECHAR/EXECUTAR | lei de forks dc-use espelhada de gc-3z7pc.1 |
| ag-p4a.1–.5 | P0/P1 | FECHAR como duplicatas | espelham ag-p4a.6–.10 fechadas (títulos idênticos) |
| ag-xqls | P2 | FECHAR | substituto `test_catalog_structure.py` landed |
| ag-f5z6 | P1 | INTEGRAR→FECHAR | review APPROVE; script+teste ao vivo |
| ag-pnif | P1 | LANDING→FECHAR | skill publicada+aplicada; blocker `flext-get3j` externo documentado |
| ag-blh | P0 | FECHAR (owner-correction) | resolução vive no ai-hub (closure plan 20260910) |
| ag-7hz | P0 | MEDIR→FECHAR/RE-ESCOPE | wheel force-include `docs/` — validar AC de empacotamento |
| ag-bak | P1 | VALIDAR→FECHAR | rescoped: headroom da cápsula no check (audit imprime snapshot) |
| ag-8oar | P1 | EXECUTAR | skill FlextCli declarativo + model-as-command (operador 17/09) |
| ag-dhzb | P1 | EXECUTAR | skill settings vs config |
| ag-07tj | P1 | EXECUTAR | skill composição FlextService |
| ag-1b5 | P0 | ADJUDICAR | derivação de lane por cwd pós-corte de-provider |
| ag-9xp | P1 | MANTER (sessão ativa) | nota de estado |
| ag-a11 | P2 | EXECUTAR se couber | precedência + routing estrito |
| ag-2sc | P0 | MANTER aberto | único filho vivo é ag-2sc.3 [E] |
| ag-zrh.4 | P1 | MANTER aberto | bloqueio externo (deploy ai-hub) registrado |
| ag-vmn | P0 [M] | ATUALIZAR notes | canônico passa `python3 -I -S --help` (sha256 novo); bloqueio = X-52/deploy ai-hub |

## 4. Beads [M]/[E] — dono externo (registro, não execução)

- **ai-hub**: ag-bwqu, ag-ey2k, ag-nq7q, ag-r0g3, ag-q4w1, ag-m9lu, ag-ssut, ag-fwdu,
  ag-k89, ag-whr, ag-q6uo, ag-2sc.3, ag-lw57 (épico) + filhos .2/.3/.4/.5/.6/.7/.8/.9/.10,
  ag-vblj (épico) + filhos .1–.5.
- **flext / flext-infra**: ag-bgs (deferred), ag-av2 (deferred), ag-ssut (sinal W1/W4),
  par `mayor` duplicado (handoff da lane flext), tríplice `flext-law` (F5 do rework).
- **multi-repo**: ag-vdl (deferred, varredura cross-project).

## 5. Higiene do tracker (18/09)

- `bd lint`: 1 warning — ag-q6uo sem "Steps to Reproduce" (bug externo flext-infra;
  aceito, o dono detalhará lá).
- `bd find-duplicates --limit 0`: 2 pares (ag-vblj.5×.4, ag-vblj.4×.3) — **mesma
  classe, defeitos distintos** (k8s-mcp × github × ast-grep): manter separados.
  Os pares reais de duplicação (ag-p4a.1–.5) não são flaggados porque os gêmeos estão
  fechados; fechamento como duplicate na F6.
- `bd doctor`: 71 passed + aviso de Dolt uncommitted — `bd vc commit` roda no fecho da
  campanha (após os updates de F6). Sem `bd dolt push` sem autorização.
- As beads da lane AH v2/SSOT não usam comentários (evidência em notes/descrição) —
  padrão respeitado nos updates desta campanha.

## 6. Guarda de gate registrada (F0)

Ponto-cego do testmon: `tests/test_projection.py:110` (budget da cápsula) não roda
quando só `rules/**` muda — o testmon não rastreia markdown como dependência. Regra
da campanha: **`make test-full` (execução real) obrigatório em toda fronteira de fase
que tocar `rules/`/`skills/`/`AGENTS.md`/`config/`**, e o resultado incremental
cache-hit nunca é reportado como prova (lei 14). Mudança estrutural no grafão do
testmon fica registrada como follow-up upstream (ferramenta, dono flext-infra).
