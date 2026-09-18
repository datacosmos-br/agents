---
description: Never deduce or guess — research, understand, and stop to ask when in doubt
capsule_summary: |
  Universal law (operator ruling 2026-09-16): NUNCA tente deduzir — sempre
  pesquise, entenda e, se tiver dúvidas, PARE E PERGUNTE. Nunca tente adivinhar
  ou deduzir. Every action is grounded in researched, verified fact: read the
  owner, run the read-only command, inspect the evidence. An unknown is not a
  hypothesis to act on — it is a question for the operator or a discovery task
  that resolves it before mutation proceeds.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-16","route:both"]'
---

# Never deduce: research, understand, ask (universal)

NUNCA tente deduzir. Sempre pesquise, entenda e, se tiver dúvidas, pare e pergunte.
Nunca tente adivinhar ou deduzir.

1. Before any action whose ground is not already verified fact, research the owner: read
   the code/config/docs, run the read-only command, inspect the actual output.
   Understanding precedes action.
2. Acting on a guess, plausibility, pattern-completion, or "most likely" is a defect
   even when it happens to work: the same move under different conditions silently
   destroys work. Deduced grounds are red grounds.
3. A genuine unknown stops the lane: one precise question to the operator, or one
   discovery task that converts the unknown into verified fact, precedes any mutation.
   "Stop and ask" is a completed step, never a failure.
4. This composes with `validate-on-change` (runtime is the proof) and
   `full-landing-cycle` (the cycle defines completion): research grounds the action,
   runtime validates it, the cycle delivers it.

See also: `validate-on-change.md` (rule file), `full-landing-cycle.md` (rule file),
`discovery-before-decision.md` (rule file).
