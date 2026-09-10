---
description: Run governance bundle audit and print inventory counts.
---

Run `make audit APPLY=Y` to load `GovernanceBundle` and print the complete
public semantic inventory: skills, commands, agents, and rules counts.

The audit output includes exact counts for every artifact type. Verify that
the counts match the AGENTS.md header: 121 skills, 12 commands, 64 agents,
56 rules. Any mismatch is a blocking violation against the canonical
inventory rule.
