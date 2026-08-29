# Cosmos GitOps delivery procedure

## Resolve authority and ownership

1. Enter the authorized physical repository, read its `AGENTS.md`, manifests,
   chart/GitOps guides, Make surface, CI, schemas, policies, tests, and current
   consumers. A contained submodule is an independent repository and lands first.
2. Identify the canonical chart, values, cluster/global configuration, generator,
   Application/ApplicationSet, or policy that owns the intended state. Rendered
   manifests and live objects are consumers, not writable sources.
3. Separate repository mutation, external publication, and cluster/environment
   mutation. Obtain explicit authority for each boundary. Resolve required review,
   exact context, staged SHA, target environment, credentials, observable health,
   and soak criteria before the corresponding effect.

Absent or conflicting authority, credentials, context, ownership, or review stops
with zero effects. Read credentials only from the declared environment; keyrings,
profiles, alternate contexts, and credential fallback are forbidden.

## Change the declarative owner

- Prefer Helm/GitOps configuration and upstream controllers for transport and
  reconciliation. FLEXT owns reusable process/config/schema/template plumbing;
  Cosmos owns only Datacosmos topology, access intent, rollout risk, render
  hygiene, and other domain policy.
- Keep cross-cutting domains, targets, issuers, routes, and topology in their
  cluster/global SSOT and shared declared helpers. Do not re-encode the same fact
  in Python or per-application values.
- Change generator input, chart source, or declarative configuration rather than
  generated/rendered output. Keep versions and business rules in their declared
  typed owner and remove a superseded route in the same cutover.
- Use Vault and External Secrets Operator references for secrets. Never commit,
  decode, render, log, or include secret material in evidence.
- Serialize every Helm operation through the repository's canonical lock and
  command surface. Do not parallelize repository state, release queues, gitlinks,
  environment promotion, or cluster mutation.

## Prove the staged artifact

Run native lint, schema, policy, render, values, integration, and security gates
for the exact staged revision. Render twice and require an unchanged second pass.
Inspect resource identity, namespace, ownership, selectors, immutable fields, sync
waves, RBAC, security context, resources, persistence, disruption behavior, and
secret references with the real declared consumer.

When live comparison is authorized, compare desired, rendered, and live state and
classify every difference before sync. Unknown or degraded state, a policy failure,
or incomplete evidence is a hard stop; it is never normalized into drift accepted
by default.

## Integrate and promote

Commit, review, merge, and post-merge validate the member repository before
updating its umbrella gitlink to the proven integrated SHA. Validate the root
projection and combined runtime separately after the pointer change.

Cluster promotion requires its own explicit authority and proceeds sequentially:
`dc-dese`, then `dc-prod`, then `dc-control`. At each authorized stage, inspect the
diff, obtain required review, invoke the canonical sync, prove health and endpoints,
and complete the declared soak before advancing.

Stop on the first failure. Preserve diagnostics, correct the declarative canonical
owner forward, rerender, rerun local gates, and repeat only the failed authorized
stage. Never deliver a live-only patch, revert or roll back repository history,
promote past red, or mix unrelated changes into failure repair. Separately
authorized emergency live remediation remains temporary and cannot satisfy the
durable landing contract.
