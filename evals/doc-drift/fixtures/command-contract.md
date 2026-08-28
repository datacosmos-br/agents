# Documented claim

The guide says: `gc sling worker work-42 --on feature`, then `gc done` commits,
pushes, and merges the change automatically.

# Canonical static owner

- `gc sling <agent> <work> --on <formula>` dispatches work only.
- The repository owns branch, commit, push, review, and merge.
- `gc done` and `gc commit` are not declared commands.
- Runtime inspection is suspended; only static owner comparison is allowed.
