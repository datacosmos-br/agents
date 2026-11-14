# Scenario: ingest dataflow view

- Repository origin: `git@github.com:example-org/ingest.git` (private, SSH).
- Lane worktree is clean; code-review-graph status reports `built_at_commit`
  equal to `current_sha`.
- Components: `ingest/api.py` (HTTP entry), `ingest/queue.py` (job queue),
  `ingest/worker.py` (consumer), `ingest/store.py` (PostgreSQL writer).
- The worker reaches the store through a plugin registry loaded at runtime.
- Requested view: dataflow from HTTP request to stored row, saved as
  `ingest-dataflow`.
- The first gate receipt lists two `supportedFixes` and one unsupported finding.
