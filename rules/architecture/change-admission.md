---
description: An architectural change, and any statement of what a rule, a check result or a check configuration is, carries full proof before it is proposed or relied on
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-14","route:both"]'
---

# Change admission

An architectural change, and any claim about the architecture, is admitted only with all
of this written where it is proposed, in every session, agent, plan, project and
discussion ([law](../law.md) 1, `operator-order-2026-11-14-architecture-change-admission`):

1. the governing decision record, guide and tracker read, and the history of the code
   under change searched for an earlier decision on the same point;
2. the mechanism stated from source, each claim with `file:line` or an executed probe;
3. behaviour measured on the declared versions of every tool that checks the code (type
   checkers, linters, the model library), with what no tool can see said plainly;
4. every option, with the reason each rejected one fails;
5. an independent review that tries to falsify the recommendation with probes;
6. the affected population counted whole, never sampled;
7. the decision record amended and approved by the operator before any code;
8. the tests that must exist before landing, by name;
9. proof at the real entry point of a real consumer.

A statement used as truth needs the same proof. What a rule says is quoted from its
branch-matched owner with `file:line`, never from memory, a summary or another agent's
report; two texts that disagree are both quoted and the authority order decides. What a
check reports carries its command, directory, tool version, selected configuration, exit
and receipt, and is never extended beyond the repository, phase and gates that ran. What
a check configuration is or should be is read from its source of truth and from the
rendered projection, both cited; changing it needs this admission and the operator's
ruling on that key.

A statement without this proof is labelled unverified where it is made and justifies no
edit, merge, closure or rule change. Relaxing a failing rule, skipping an input, adding a
fallback, widening a type only to silence a check, or landing unfinished work on an
integration branch is a workaround ([law](../law.md) 6, 8, 9, 10). Review rejects it from
any author; only the operator's ruling on that point admits one.
