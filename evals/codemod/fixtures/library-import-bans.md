# Catalog scenario — library import bans

A repository's ast-grep catalog has these four rules. Each sits in `rules/` with its
own `tests/<id>-test.yml` and snapshot:

```yaml
id: ban-direct-ldap3-import
language: Python
severity: error
message: Import ldap3 only through the LDAP facade.
files: ["src/**/*.py"]
rule: { pattern: import ldap3 }
---
id: ban-direct-oracledb-import
language: Python
severity: error
message: Import oracledb only through the database facade.
files: ["src/**/*.py"]
rule: { pattern: import oracledb }
---
id: ban-direct-structlog-import
language: Python
severity: error
message: Import structlog only through the logging facade.
files: ["src/**/*.py"]
rule: { pattern: import structlog }
---
id: ban-direct-gitpython-import
language: Python
severity: error
message: Import git only through the Git facade.
files: ["src/**/*.py"]
rule: { regex: 'import git' }
```

A reviewer reports a new violation: `from requests import Session` in
`src/pkg/client.py`, where the HTTP facade owns `requests`. This repository's `make help`
declares `make mod` (applies rules and verifies committed snapshots) and
`make mod-snapshots` (the only verb that regenerates rule-test snapshots). It declares
its facade-owned libraries in a typed configuration owner that the rule engine can read
as a context predicate.

The installed engine already exposes a cached workspace module model, change
invalidation and semantic rename through generic capability ports. The proposed fix
adds a second parser and one rule per library. Compatible uncommitted consumer changes
are present; a teammate wants to stop until the checkout is clean. The required public
result is preserved symbol identity after rename, refreshed references after a source
change, and a second run with no additional effects.
