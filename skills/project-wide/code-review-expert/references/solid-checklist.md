# SOLID review adapter

Use the canonical `solid` skill as the sole authority for SRP, OCP, LSP, ISP,
DIP, their evidence requirements, remediation boundaries, and relationship to
`search-first`, `simplify`, and `dry`. Do not reproduce a second checklist here.

In review-only mode:

1. Apply `search-first` to the changed architecture, owners, callers, behavioral
   contracts, and composition root.
2. Apply `solid` without mutating files. Cite the decisive file and line for each
   confirmed violation and identify the observable change risk.
3. Assign severity from runtime impact: correctness, security, broken
   substitutability, or unsafe dependency direction may block; pattern preference,
   size alone, or a hypothetical future variant is not a finding.
4. Route confirmed duplicated knowledge, dead paths, god ownership, and repeated
   work to `dry`; route local readability and needless control flow to `simplify`.
5. Recommend the smallest owner-correct remediation and the contract/runtime test
   that proves it. Never recommend factories, interfaces, plugins, inheritance,
   or layers without a real current consumer.

The review reports evidence and remediation; it does not implement until the user
explicitly authorizes changes.
