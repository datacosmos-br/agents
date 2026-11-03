# Deletion inventory

- `build/report.json`: tracked generated output; owner command is `make clean`.
- `notes/operator-draft.md`: untracked operator draft with unknown ownership.
- `src/replacement.py`: tracked final owner required by the approved cutover.
- `src/legacy.py`: tracked superseded owner; `src/api.py` is its only consumer and must
  be rewired to `src/replacement.py` in the same patch.
- Tests and fixtures named `legacy` protect only the superseded contract.
- `legacy-provider-surfaces/` is an approved untracked payload to move to
  `agents.legacy` on the same filesystem. It contains `hooks/old`, a symlink to
  `../../active/hooks`, and a regenerable `.venv` subtree that is never copied.
