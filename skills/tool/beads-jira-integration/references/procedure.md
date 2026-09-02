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
`httpx`). Credentials come from `secret-tool` via `u.Cli.run_raw` at the
service boundary only — never from settings, config, or environment variables.
The first exception escapes; no retry, no fallback, no catch-to-None.

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
