---
description: Remote access follows the declared Git identity; agents never write SSH configuration
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-11-02","route:both"]'
---

# Remote identity

Remote access follows current Git/forge configuration. Never rewrite protocols,
create identity aliases or change user SSH configuration for Git operations. A broken
alias never authorizes a generic remote: preserve the declared identity and repair
through its owner. Agents never write operator SSH configuration or keys, including
repair, fragment deployment or access restoration. Correct identity in Git; report
required SSH configuration changes to the operator.
