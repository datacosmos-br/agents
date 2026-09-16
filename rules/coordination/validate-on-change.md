---
description: Validate-on-change — the only proof is full functioning in runtime
capsule_summary: |
  Universal law (operator ruling 2026-09-16, effective immediately): ao criar ou
  alterar alguma coisa, valide se está certo e funciona — o que vale
  fundamentalmente nunca é tests simples ou evidências: é o PLENAMENTE
  FUNCIONAMENTO EM RUNTIME. Every write is followed in the same grain by
  exercising the real runtime path the change claims to affect — the real
  imports, the real verbs, the real product flows — until the behavior is
  observed working end to end.

  Simple tests, green gates, and evidence artifacts are necessary bookkeeping,
  never the proof. A change proven only by tests but not observed functioning in
  the real runtime is NOT validated and NOT landed.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Validate-on-change: runtime functioning is the only proof (universal)

Ao criar ou alterar alguma coisa, valide se está certo e funciona. O que vale
fundamentalmente nunca é tests simples ou evidências: é o pleno funcionamento
em runtime.

1. Every creation or change — source, config, template, doc, generated
   artifact — is validated in the SAME grain that produced it.
2. Validation = exercising the REAL runtime path end to end and observing the
   claimed behavior happening: import the real package, run the real verb,
   execute the real flow, consume the real artifact. Tests and green gates are
   bookkeeping around this; they are never substitutes for it.
3. The runtime observation (command, working directory, exit code, decisive
   runtime output) is recorded with the change. No runtime observation, no
   completion.
4. A change not yet observed functioning in runtime is not landed: record the
   exact blocker and stop that grain.
5. This composes with runtime-is-reality and strict execution; where tests
   disagree with observed runtime behavior, runtime wins and the test is
   corrected or removed.
