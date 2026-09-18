# Handoff da campanha agents — 2026-09-18 (agente dedicado único)

> Campanha executada sob mandato do operador (agente único dedicado, fix-forward-adopt,
> colaboração com lanes paralelas por registro). Escopo duro: repo `agents` + DB beads
> `ag`. Nenhum arquivo de outro projeto foi editado. Fases F0–F7 do plano aprovado
> (pergunta-a-decisão: código alinhado ao contrato; `~/.agents` desymlinkado como
> projeção global; push autorizado no fecho).

## 1. Estado entregue (tudo medido em runtime no SHA final)

- **Gates**: `make setup`/`gen`×2/`fmt`/`fix`/`check`/`test`/`ci`/`build`/
  `validate-artifacts`/`runtime` — todos EXIT=0 no ciclo frio revalidado. `test-full`
  = 63 passed com execução real (`executed=63 deselected=0`); `home-check` 1340
  arquivos verificados. rumdl 543/543 limpo. waza 137 skills / 265 arquivos verde.
- **F0** (`a1213d2c`, `28b76f42`): budget da cápsula destravado — causa-raiz real era o
  reflow do prelude em `6978f43c` (+40 chars; NÃO o `d08439df` como se suspeitava);
  prelude restaurado (9450/9488, headroom 38); 2 references condensadas sob o teto
  waza. Ponto-cego do testmon registrado (§4).
- **F1** (`4a1659b1`): handoff zcode recuperado — **não-criação, não perda**; sessões
  `sess_b22e8d6c`/`sess_a97a9cb3` consolidadas em
  `20260918-handoff-zcode-catalog-sessions.md` com pendências dono-nomeadas.
- **F2** (`0d60299d`): `20260918-status-ledger.md` publicado (veredito plano-a-plano,
  grafo de bloqueio, 59 beads classificadas [A]/[M]/[E]); headers stale retificados
  (reval-closure EXECUTADO via PR #133 `ab27a954`; pydantic atualizado).
- **F3** (`19e64c01`, `8f73e34e`): ADR-0008 cumprido no pacote — `cli.py`/`__main__.py`
  removidos, `projection.py` → `tools/governance_projection.py` (dev-only); **wheel
  0.5.0 provado sem cli/__main__/projection, 18 módulos, 248 recursos exatos, sem
  entry_points**; zero importadores externos (medido). ADR-0022 escrito antes da F4.
  Resíduo `.kilo/` adjudicado (command/agent removidos com contagens stale;
  `kilo.json` mantido — config do operador).
- **F4** (`2be349fa`, `62287f22`): `~/.agents` desymlinkado com backup
  (`~/.agents-archive/home-desymlink-2026-09-18/`) e materializado como projeção
  global de leitura (11 árvores, manifesto versão+digest). `home-sync`/`home-check`
  wired no `check` — **a gate pegou drift real na primeira mutação do catálogo** e o
  `home-sync` convergiu varrendo resíduo do WIP antigo com receipt. `AGENTS.md` entrou
  na projeção por consumidor medido (ssot_relink + `projection_identity_gate`
  fail-closed do ai-hub). **WORKAROUND marcado no Makefile**: verbos locais pendentes
  de adoção pelo codegen flext-infra (lane paralela); idem os 3 knobs de analisador no
  pyproject (pythonpath/extraPaths/mypy_path = tools).
- **F5** (`e16681a6`): vocabulários fechados viraram config-dado — `skills.json` v3 com
  seção `vocabulary` (usage/routes/activation/subjects; sorted-unique, prefix-check,
  slug-check); constantes `_SUBJECTS` etc. removidas do código; validação fail-closed
  mantida. X-52 medido: canônico `op-learning/references/` íntegro — o drop é ai-hub.
- **F6** (18 fechamentos com evidência + `bad28882`): fechadas com evidence-chain
  ag-aq8, ag-vky, ag-22s, ag-xqls, ag-f5z6, ag-pnif, ag-blh (owner-correction), ag-7hz
  (meia provada + meia moot pelo corte ADR-0008), ag-bak (headroom impresso no audit —
  `--force` sobre aresta stale), ag-1b5 (premise gone), ag-p4a.1–.5 (duplicatas),
  ag-8oar/ag-dhzb/ag-07tj (conteúdo: model-as-command com grounding real no
  flext-infra; settings-vs-config nova; flext-service reescrito sobre contrato provado,
  WIP não-provado varrido). ag-vmn: notes atualizadas (canônico portável provado,
  bloqueio real = projeção ai-hub).
- **Tracker**: 250 beads — 26 open, 11 in_progress, 3 blocked (ag-vmn, ag-m9lu,
  ag-zrh.2), 209 closed. Dolt commit `miujh6vv`. Restantes [A] conscientes: ag-9xp
  (sessão ativa), ag-a11 (P2), épicos ag-2sc/ag-zrh/ag-lw57 vivos por filhos externos.

## 2. Pendências externas (dono nomeado — registro, não execução)

- **ai-hub**: preflight do deploy (wheel staging vazio) → redeploy claude/skills
  (espelho defasado) → registro do consumidor `claude` + exclusão formal de `synced/`;
  ag-bwqu (acceptance real, único bloqueador de código do piloto), ag-ey2k (walker
  O_NOFOLLOW), ag-nq7q (CRG sync), ag-lw57.* / ag-vblj.* (AH v2/MCP), X-52
  (projeção dropa references/*), ag-r0g3, ag-q4w1, ag-m9lu (piloto), ag-2sc.3,
  ag-ssut, ag-fwdu, ag-k89, ag-whr, ag-lw57.9. Já-missing antes da transição (não
  causados por ela): `UNIVERSAL_CORE.md`, `agents/manifest.json`, `bin/mcp-run`,
  `mcp/servers.json`.
- **flext-infra** (lane paralela do operador): adotar os verbos `home-sync`/
  `home-check` + knobs de analisador no codegen (workaround marcado no Makefile/
  pyproject do agents); mudança estrutural no grafão do testmon (rastrear markdown).
- **flext**: par `mayor` duplicado (poda é whack-a-mole; runtime gc recria),
  tríplice `flext-law`, ag-bgs, ag-av2.
- **gc**: storage janitor lista `~/.agents` como repositório — reavaliar pós-projeção.
- **multi-repo**: ag-vdl (deferred).

## 3. Fila de continuidade catalog-side

1. Consumir feedback do CI remoto do push (mesmas gates locais).
2. ag-a11 (P2) quando couber; ag-9xp pertence à sessão viva.
3. Novo intake de capabilities segue ADR-0014; novos subjects entram por
   `config/skills.json` v3 (config-dado), nunca por constante.
4. Quando o ai-hub assumir a gestão transacional do home (F6 do rework), o par
   `home-sync`/`home-check` passa a ser delegado — contrato já em ADR-0022.
5. Beads [E] só movem com as lanes donas; nada de falso fechamento catalog-side.

## 4. Guardas permanentes registradas

- **testmon não rastreia `rules/**`/`skills/**`/`AGENTS.md`**: em qualquer fronteira
  que toque markdown/config, `make test-full` (execução real) é obrigatório —
  cache-hit incremental não é prova (lei 14).
- **Budget da cápsula é contrato**: corrige-se conteúdo, nunca teto (10000/512).
- **Escrita de consumer em `~/.agents` é defeito reportado** (ADR-0022); reparo é
  `make home-sync`, nunca restauração do symlink.
- **Commits pathspec-escopados; push de `dev` autorizado nesta campanha apenas.**
