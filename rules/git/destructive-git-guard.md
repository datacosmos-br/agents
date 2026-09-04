# Never run destructive git on shared or unknown changes

Two `git reset` runs wiped multi-agent worktrees (and nearly the `.beads` DB).
Against a shared tree or changes you did not author, these are forbidden:

`git reset`, `git checkout -- .`, `git restore`, `git clean -xdf`/`-Xdf`,
`git stash drop`, `git rebase`, `git push --force`.

- Stage only your own paths (`git add <scoped paths>`); never `git add -A`/`.`
  at a workspace or umbrella root.
- Fix forward: recover from `git reflog`, never by discarding others' work.
- Commit often so your work survives another lane's mistake.
