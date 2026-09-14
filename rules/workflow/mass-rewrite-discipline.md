---
description: Tree-wide mechanical rewrites and automation-applied fixes are commit-boundaried, inventories-first, and fully test-proven before and after.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Mass rewrite discipline: inventory, boundaries, evidence

Any transformation applied to more than a handful of files — textual rewrites
(`sed`/regex), ast-grep batch application, enforcer or codemod `apply` cycles,
bulk import/annotation migrations — is a production effect with the same
standing as a code change, not free bookkeeping. It is graded like code.

- **Test evidence brackets the rewrite.** `make test` runs before and after the
  mass, not only after. Static gates green do not prove runtime: annotations
  evaluated by frameworks (pydantic, casts, generics), string literals, and
  fixtures can break only at runtime. A mass landing without a post-run test
  selection result is an unproved trunk.
- **Commit boundaries are part of the change.** Never accumulate tree-wide
  uncommitted mass. Package the rewrite into scoped commits (owner of the
  transformation, not file adjacency) and push each package; a trunk with a
  large uncommitted delta has no identifiable state, no rollback, and blocks
  concurrent lanes.
- **Inventory the applied/reverted state.** Automation that applies and
  conditionally reverts per gate (enforcers, fixers) leaves mixed states.
  Before any commit, enumerate exactly what was applied and what was reverted
  per transformation, decide keep/revert per group, and propose the point
  fixed point. Uninventoryable apply/revert spray is a defect.
- **Context-safety of the rewrite engine.** Textual substitution without
  annotation/string-context discrimination is suspect by default: a
  machine-checkable string-literal sweep over the touched tree is part of the
  change's proof, checked manually per suspect hit.
- **Conformance progress is reported by violation class.** Fixing the
  mechanical class (annotations, aliases) while structural classes
  (nesting, facades, module shape) stand untouched is not aggregate progress;
  declare counts per class, and let the structural classes own the remaining
  phase plan.
- **Tracker evidence cadence.** Each class landed updates the campaign tracker
  item in the same session with command, counts, and decisive output; a
  campaign without per-step tracker evidence is not a campaign.

Compose with `rules/workflow/structural-migrations.md` (rule layering),
`rules/workflow/production-readiness.md` (blast-radius adoption),
`rules/runtime/strict-execution.md` (atomic effects), and
`rules/workflow/beads-traceability.md` (evidence cadence).

## §Templates — cirurgia em templates gerenciados (2026-09-11, do erro real)

Template gerido (`.j2` em `src/flext_infra/templates/`) é CÓDIGO PRODUÇÃO com
história, não scratch. Proibido reescrever do zero. Obrigatório:

1. **Diff cirúrgico primeiro**: remover só os blocos da transformação
   (define/calls/condicionais). Reescrever 732→467 linhas destruiu bootstrap
   mise, resolução UV do caller, exports, cygpath — ~400 falhas em cascata.
2. **Contexto de render = campos do RenderSpec**: cada `{{ var }}` no template
   tem que existir no modelo de render (ex.: `MakefileRenderSpec`). Antes de
   referenciar variável: ler o modelo em `_models/config.py`. `'dict object' has
   no attribute 'X'` = variável inventada ou campo removido do SSOT.
3. **Quebra de render = sintoma de dono**: `{% if verb.requires_apply %}` refere
   campo removido de `MakeVerbSpec` — consertar no template É o passo do
   exterminio; a remoção do campo no SSOT exige a cirurgia nos templates NO
   MESMO commit.
4. **.bak dentro de templates/ é defeito**: descoberta de templates enumera o
   diretório; staging nunca no repositório.
5. **Descriminar flag de ambiente de arg CLI**: o antigo flag de ambiente que
   exigia confirmação foi exterminado — cada verbo Make executa diretamente
   sua operação, sem seletor de aplicação; `--apply` (arg interno
   de CLI em release/codegen init/deps) é contrato interno vigente distinto —
   não confundir, não remover.
6. **Prova por render**: qualquer mudança de template exige
   `pytest <framework de conform>` até ponto fixo, nunca "deve renderizar".
