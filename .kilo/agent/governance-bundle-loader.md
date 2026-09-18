---
description: Load and inspect the governance bundle from the canonical source.
mode: primary
permission:
  read:
    "*": allow
  edit:
    "*": allow
  bash:
    "*": ask
    "make *": allow
    "ls *": allow
    "git *": allow
---

Loads `GovernanceBundle` from `agents_governance` and inspects the complete semantic
inventory: skills, commands, agents, rules, agent profiles, and approval lineage. Use
this agent when you need to audit governance artifacts or verify inventory counts
against AGENTS.md declarations.
