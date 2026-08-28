# Newest operator instruction wins; adjust artifacts to it

Authority order: operator request > declared orchestration contract > canonical
tracker > ADRs > skills > docs, and newest supersedes oldest. On conflict,
adjust the lower or older artifact to match; never override the operator to
satisfy stale guidance.

While orchestration and tracker runtimes are suspended, do not invoke them or
create a substitute ledger. Preserve implementation evidence in Git/PR/CI and
leave phase closure open.

When authority genuinely conflicts or an action is destructive, ask one precise
question first. Otherwise continue. Never guess on ambiguity.
