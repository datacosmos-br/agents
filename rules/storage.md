# Storage and scratch law

This file owns universal storage placement. Project and skill documents point
here and add only narrower local constraints.

`config/storage.toml` is the sole writable owner of storage paths and runtime
limits. Every required path is absolute, expanded, typed, and validated before
the first effect. Code, environment, and documentation consume its stable keys;
they do not carry independent operational defaults.

- `/tmp` is limited to small, bounded operating-system ephemera. Never place a
  repository, worktree, virtual environment, persistent database, build cache,
  checkpoint, backup, or report there.
- `agentsctl check` owns each test/build child and a physical run directory
  under the configured repository scratch owner. It validates the entire child
  graph before spawning and supplies distinct, already validated `TMPDIR`,
  `GOTMPDIR`, and `GOCACHE` paths.
- Reusable caches belong to the exact configured XDG cache owner. Node compile
  caches use `NODE_COMPILE_CACHE` under this hierarchy.
  `GOMODCACHE` is shared; execution/build scratch is not.
- Persistent evidence belongs to the exact configured XDG state owner. Shells
  and managed children receive only paths already validated from the typed
  owner. Missing, empty, conflicting, unexpanded, or invalid required variables
  raise; no shell or home-directory fallback exists.
- `agentsctl clean` is fail-loud. It validates the complete candidate and
  preservation set before deleting anything. Preserve runs younger than
  `policy.orphan_age_days` and
  anything with a live lock, process ownership evidence, Git/venv/database
  content, symlink, or unknown entry. The configured retention may never be
  shorter than the universal seven-day safety invariant. Never use `rm -rf`,
  `git clean`, reset, or stash for GC.
- `policy.failure_bytes` bounds each owned run. Crossing it raises and a limiter
  may signal only the child process group it created.
- `policy.report_max_bytes` bounds report publication. Capacity failure keeps
  prior reports and the current scratch evidence; it never prunes evidence.
- A successful owned child is not an orphan: after its report is persisted, its
  marked run tree is removed immediately. Failed/interrupted runs remain for GC.
- Preflight selects exactly one supported physical copy primitive for the
  destination filesystem. Its failure raises; no alternate copy primitive is
  attempted. Copies remain independent physical trees; symbolic links and
  cross-repository references are prohibited.

Canonical surface:

```text
agentsctl check
agentsctl clean
```
