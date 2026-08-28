# Build-cache release notes

- Audience: platform engineers maintaining polyglot CI.
- Median clean build before: 11 minutes 40 seconds.
- Median warm build after: 4 minutes 12 seconds.
- Measurement: the same 28 repositories, five runs per repository.
- Mechanism: cache keys combine compiler version, lockfile digest, and target platform.
- Safety: a missing lockfile disables reuse instead of falling back to a broad key.
- Limitation: two repositories were excluded because they have no lockfile owner.
- No customer cost data, quotes, or production incident-rate claims were collected.
