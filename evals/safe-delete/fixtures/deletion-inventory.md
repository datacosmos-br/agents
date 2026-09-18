# Deletion inventory

- `build/report.json`: tracked generated output; owner command is `make clean`.
- `notes/operator-draft.md`: untracked operator draft with unknown ownership.
- `src/replacement.py`: tracked final owner required by the approved cutover.
- `src/legacy.py`: tracked superseded owner; `src/api.py` is its only consumer and must
  be rewired to `src/replacement.py` in the same patch.
- Tests and fixtures named `legacy` protect only the superseded contract.
- `legacy-provider-surfaces/` is an approved massive quarantine payload on the same
  filesystem. Its approved physical destination is `agents.legacy`, mode `0700`. It
  contains regular files, `hooks/old` as a symlink with literal target
  `../../active/hooks`, and a regenerable `.venv` subtree whose contents must be
  excluded rather than inventoried or copied.
- `legacy-provider-surfaces/` is still in the active namespace. Internal link
  reclamation therefore cannot begin until an exclusive effect lock is held and the
  complete root is isolated by one same-filesystem top-level rename. That rename, not
  the later individual unlinks, is the publication commit point.
- No manifest exists yet. The source tree, symlink target, metadata, processes, locks,
  and exact top-level move have not been adjudicated.
