# Dolt endpoint law

- Gas Town owns the only production Dolt server: `127.0.0.1:3307`.
- Every town, rig, crew, polecat and agent metadata file must select that endpoint and its routed database.
- `dolt.shared-server`, `bd --global`, alternate ports, alternate hosts and standalone `bd dolt start` are prohibited.
- `BEADS_DOLT_SHARED_SERVER` must be absent. Any Dolt port environment variable, when present, must equal `3307`.
- A phase cannot land while `make dolt` reports config, metadata, environment or live-listener drift.
- Tests, fixtures, caches and scratch have no exception: they must use the Gas Town server on `127.0.0.1:3307` or avoid Dolt entirely.
