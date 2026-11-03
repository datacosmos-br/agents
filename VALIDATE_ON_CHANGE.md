# Governance repository validation

This guide applies to the `agents-governance` repository. [The law](rules/law.md) and
[canonical commands](rules/workflow/canonical-commands.md) own execution, deadlines,
test selection and phase closure; this guide does not restate them.

## Public surfaces

| Operation | Root verb | Evidence supplied |
| --- | --- | --- |
| Catalog and context budget | `make audit` | Validated public bundle inventory and calculated delivery margin |
| Documentation | `make docs` | Catalog validation, ADR identities and relative links |
| Semantic suite structure | `make waza` | A second generation that changes nothing, token budgets and every suite's specification coverage |
| Complete non-test acceptance | `make check` | Documentation, code/resources, structural rules, workflows, duplication and isolated artifacts |
| Incremental tests | `make test` | Native testmon selection or integrity-checked cache-hit accounting |
| Complete local tests | `make test-full` | Entire local suite; existing testmon database preserved |
| Resource analyzer profile | `make profile-mypy-resources`, `make profile-mypy-resources-report` | cProfile data for the declared resource population |
| Semantic gate profile | `make profile-waza`, `make profile-waza-report` | Coordinator cProfile and total wall time; child code is not instrumented |

Inspect `make help` before invoking an operation. Use an existing, valid environment;
setup provisions when required and exclusive ownership is proved.

Specification coverage and artifact installation validate the package contract.
They do not prove that AI Hub published a provider surface, withdrew its old copy,
or that a native agent loaded it. Those receipts belong to AI Hub's delivery owner.

Record the changed owner and consumers, command, cwd, exit, decisive output and
source revision on the selected available tracker task. When that tracker is
unavailable, preserve receipts only through separately authorized Git/PR/CI and
leave closure open. Integrate the exact candidate through
[branch and pull request](rules/git/gitflow-branch-pr.md); a source receipt never
replaces a merged revision or an installed runtime receipt.
