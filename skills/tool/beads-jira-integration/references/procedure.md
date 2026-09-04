# Epic-Link Gap Procedure

The `bd jira sync` CLI does not set `parent` on created Jira issues. To link
created issues under a Jira epic, implement the FLEXT service below. It is the
only custom code allowed in the integration.

## Service

`CosmosMainJiraService(s)` in `src/cosmos_main/services/jira.py` with:

- `fetch_unparented() -> r[Sequence[m.JiraIssueRef]]` — list Jira issues
  without a parent that belong to the configured project.
- `link_to_epic(plan: JiraLinkRequest) -> r[Sequence[m.JiraLinkPlan]]` —
  set `parent` on each issue via `u.Cli.run_raw(("curl", ...))`.

HTTP calls use `u.Cli.run_raw` (never `urllib.request`, `requests`, or
`httpx`). Credentials come from the beads CLI config (`bd config get
jira.api_token`) — never from settings, config YAML, or environment variables.
The first exception escapes; no retry, no fallback, no catch-to-None.

## Recovery Runbook: bad push created duplicate/unparented tickets

1. Inventory the damage (needs the operator-set API token):
   JQL `project = COSM206 AND parent IS EMPTY AND created >= "<sync-date>"`.
2. Decide per ticket: the ledger's `external_ref` copy is canonical; strays
   transition to Done with comment
   `duplicate from sync <date>; canonical mirror is <key>`.
3. Re-sync only what is open:
   `bd jira sync --push --state open --dry-run`, review, then run for real.
4. Prove: `bd jira status` shows a dated Last Sync and Local-Only count that
   matches the intentionally-unpushed set (closed beads and bugs).

## Model

`src/cosmos_main/_models/jira.py` — declaration-only Pydantic 2 models:

- `m.CosmosMain.JiraIssueRef(key: str, summary: str = "")` — frozen.
- `m.CosmosMain.JiraLinkPlan(bead_id: str, jira_key: str, epic_key: str)` — frozen.

## Protocol

`src/cosmos_main/_protocols/jira.py`:

- `p.CosmosMain.JiraLinkRequest` — `Protocol` with `epic_key: str` and
  `issue_keys: Sequence[str]` read-only properties.

## Settings and Config

Settings fields in `src/cosmos_main/_models/settings.py`:

```python
jira_base_url: str = ""
jira_project_key: str = ""
jira_epic_key: str = ""
```

Config values in `src/cosmos_main/config/cosmos-main.yaml`:

```yaml
jira:
  base_url: https://datacosmos.atlassian.net
  project_key: COSM206
  epic_key: COSM206-148
```

## MRO Registration

Add `CosmosMainJiraService` to the `CosmosMainApi` cooperative MRO in
`src/cosmos_main/api.py`. Update lazy exports in `src/cosmos_main/__init__.py`.

## CLI Adapter

`scripts/jira/link_epic.py` — thin `flext_cli` adapter. Calls
`cosmos_main.link_to_epic()`. Zero business logic. Zero HTTP calls. Zero
credential handling.

## Verification

1. `scripts/jira/` contains only `link_epic.py`.
2. No `__pycache__`, `.csv`, `.sh`, or legacy scripts remain.
3. `git status --short` shows only the expected FLEXT artifacts.
4. `bd jira status` confirms all features have `external_ref`.

## Sync Policy (beads is SSOT; Jira mirrors OPEN work)

- Only OPEN beads sync. Closed beads and `bug` type never create Jira issues.
- Re-push without dedup creates duplicate tickets: always `--dry-run` first,
  and keep `external_ref` as the single dedup key.
- `--parent <bead>` limits the push to one bead and its descendants.
- A push that fails to write `external_ref` back leaves orphan Jira tickets the
  ledger cannot see — audit with
  `project = <KEY> AND parent IS EMPTY AND created >= "<sync-date>"` and
  transition strays to Done with a cause comment.
- The Jira API token is operator custody: it lives in `bd config` (or
  secret-tool at the service boundary), never in transcripts, git, or env files.

## Configuration (native `bd config`)

```bash
bd config set jira.url "https://<instance>.atlassian.net"
bd config set jira.project "<PROJECT_KEY>"
bd config set jira.push_prefix "<bead-prefix>"
bd config set jira.username "<email>"
bd config set jira.api_token "<token>"
```

The beads CLI owns all Jira credentials — never source, `.env`, project YAML,
or script env vars.
