# Skills

Recursive discovery from `skills/<category>/<slug>/SKILL.md` is the identity,
category, and primary distribution authority. `config/skills.json` owns only
schema version and BPE/line budgets; it must never list skills, destinations, or
activation modes.

- `agent-wide` is always personal and `project-wide` is always project-scoped.
- `technology`, `framework`, `tool`, and `domain` are conditional groups whose
  validated tags declare route, activation, subject, and detector evidence.
- Every destination receives an independent physical copy; bundles contain no
  symbolic links, local cross-repository paths, or synchronization metadata.

Each bundle is self-contained. Keep `SKILL.md` as a concise, authored activation
router; put detailed procedures, scripts, and assets inside the same bundle.
Frontmatter descriptions contain 3-10 unique lowercase keywords or nominal
phrases separated by `, `, within 12-96 characters. They are discovery metadata,
not prose, provenance, or a duplicate procedure.

`skills.lock.json` is the sole generated inventory lock. Check it with
`make audit`; refresh it only after the last skill edit with
`make audit APPLY=Y`, then prove the unchanged check reaches a fixed point.
