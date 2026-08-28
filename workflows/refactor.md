# Workflow: refactor

## Goal

Improve structure without changing public behavior, complete the cutover, and
end net-negative in superseded implementation.

## Procedure

1. Read repository law, owners, consumers, current tests/docs, Git state, and
   concurrent WIP.
2. Discover canonical commands and capture representative runtime behavior plus
   the affected native gate baseline.
3. Use structural search and call/reference analysis to inventory the complete
   blast radius.
4. Define one behavior-preserving objective. Feature changes belong in a
   separate feature slice.
5. Build the final owner shape, migrate every consumer, and delete the old
   implementation, fixtures, examples, and documentation in the same cycle.
6. Use the `simplify` skill for behavior-preserving readability review when
   applicable; no removed slash command is assumed.
7. Re-run representative runtime, then affected native lint, format, type,
   test, build, security, and generation/fixed-point gates.
8. Prove no stale symbol, compatibility path, duplicate owner, or dead code
   remains. Review the net line change and explain any non-negative result.
9. Follow the landing contract in [WORKFLOWS.md](WORKFLOWS.md).

## Fail-closed rules

- Never refactor over a red unexplained baseline.
- No shim, adapter solely for compatibility, dual-read/write, fallback,
  suppression, or postponed deletion.
- Tests assert public behavior, not internal construction.
- Preserve unknown and concurrent WIP; never reset, stash, or force-push.
- While tracker runtime is suspended, create no substitute tracker or ledger,
  preserve evidence only in separately authorized Git/PR/CI, and leave phase
  closure open.
