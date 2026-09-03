#!/usr/bin/env python3
"""Locate, reply to, and resolve pull-request review comments via gh.

Companion tooling for the pr-sheriff skill. `locate` and `sweep` are
informational inventories; `gate` is the fail-closed landing preflight.
`reply`, `resolve`, and `settle` perform the single named GitHub effect.

Strict-execution contract: the first gh or GraphQL failure escapes with
its stderr and a nonzero exit; there is no fallback, retry, credential
handling, or success claim without the effect's own confirmation.
Dependencies: python3 stdlib and the `gh` CLI already authenticated by
the operator's shell. Never extracts or relocates credentials.

Subcommands:
  locate <owner/repo> <pr>            full blocking-check inventory (JSON)
  gate <owner/repo> <pr> --base B --head OID  fail unless exactly landable
  sweep <owner/repo>... --base B,...  integration-lane PR queue (JSON)
  reply <thread-id> --body-file F     answer one review thread
  resolve <thread-id>                 resolve one review thread
  settle <thread-id> --body-file F    reply, then resolve
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

_PASSING_CONCLUSIONS = frozenset({"success", "neutral", "skipped"})
EXTERNAL_EXECUTABLES = frozenset({"gh", "git"})
_MANAGED_PRIVATE_OWNERS = frozenset({"datacosmos-br", "marlon-costa-dc"})
_REQUIRED_PERMISSION = {"read": "pull", "push": "push", "admin": "admin"}


def _gh(*arguments: str, input_text: str | None = None) -> str:
    """Run gh in the operator's shell; propagate failure unchanged."""
    completed = subprocess.run(
        ["gh", *arguments],
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    return completed.stdout


def _external(*arguments: str) -> str:
    executable = arguments[0]
    if executable not in EXTERNAL_EXECUTABLES:
        raise ValueError(f"external executable is not declared: {executable}")
    completed = subprocess.run(
        list(arguments), capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    return completed.stdout


def managed_private_access(
    repository: str, effect: str, ssh_url: str | None
) -> dict[str, Any]:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise ValueError("repository must be exactly owner/name")
    detail = json.loads(_gh("api", f"repos/{repository}"))
    private_managed = bool(detail.get("private")) and owner in _MANAGED_PRIVATE_OWNERS
    result: dict[str, Any] = {
        "repository": repository,
        "private_managed": private_managed,
        "effect": effect,
    }
    if not private_managed:
        result["access_preflight"] = "not_selected"
        return result
    if ssh_url is None:
        raise ValueError("managed private repository requires --ssh-url")
    expected_suffix = f":{repository}.git"
    if not ssh_url.startswith("git@") or not ssh_url.endswith(expected_suffix):
        raise ValueError("SSH URL must identify the exact managed repository")
    host = ssh_url.removeprefix("git@").split(":", 1)[0]
    if not host or host == "github.com":
        raise ValueError(
            "managed private repository requires a declared SSH host alias"
        )
    permission = _REQUIRED_PERMISSION[effect]
    permissions = detail.get("permissions")
    if not isinstance(permissions, dict) or permissions.get(permission) is not True:
        raise PermissionError(
            f"GitHub permission {permission} is required for {repository}"
        )
    _external("gh", "auth", "status", "--active", "--hostname", "github.com")
    _external("git", "ls-remote", ssh_url, "HEAD")
    result.update(
        {
            "access_preflight": "passed",
            "permission": permission,
            "ssh_host_alias": host,
        }
    )
    return result


def _graphql(query: str, **variables: Any) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables})
    raw = _gh("api", "graphql", "--input", "-", input_text=payload)
    body = json.loads(raw)
    if body.get("errors"):
        raise SystemExit(f"graphql errors: {json.dumps(body['errors'])}")
    return body["data"]


def _gh_paginated(path: str, query: str) -> list[dict[str, Any]]:
    """Return every JSON object emitted by a paginated GitHub REST query."""

    raw = _gh("api", "--paginate", path, "-q", query)
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


REVIEW_THREADS_QUERY = """
query($owner:String!,$name:String!,$number:Int!,$cursor:String){
  repository(owner:$owner,name:$name){
    pullRequest(number:$number){
      reviewThreads(first:100,after:$cursor){
        nodes{
          id isResolved
          comments(first:1){nodes{databaseId author{login} body path line}}
        }
        pageInfo{hasNextPage endCursor}
      }
    }
  }
}
"""


def review_threads(owner: str, name: str, number: int) -> list[dict[str, Any]]:
    threads: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        data = _graphql(
            REVIEW_THREADS_QUERY,
            owner=owner,
            name=name,
            number=number,
            cursor=cursor,
        )
        connection = data["repository"]["pullRequest"]["reviewThreads"]
        for node in connection["nodes"]:
            first = node["comments"]["nodes"][0] if node["comments"]["nodes"] else {}
            threads.append(
                {
                    "thread_id": node["id"],
                    "resolved": node["isResolved"],
                    "author": (first.get("author") or {}).get("login", "ghost"),
                    "path": first.get("path"),
                    "line": first.get("line"),
                    "comment_id": first.get("databaseId"),
                    "body": first.get("body", ""),
                }
            )
        if not connection["pageInfo"]["hasNextPage"]:
            return threads
        cursor = connection["pageInfo"]["endCursor"]


def _checks(owner: str, name: str, ref: str) -> list[dict[str, Any]]:
    return _gh_paginated(
        f"repos/{owner}/{name}/commits/{ref}/check-runs?per_page=100",
        ".check_runs[] | {name:.name,status:.status,conclusion:.conclusion}",
    )


def checks_verdict(checks: list[dict[str, Any]]) -> str:
    """Report what the check set actually proves."""

    if not checks:
        return "not_determined"
    if _blocking_checks(checks):
        return "failing"
    if _pending_checks(checks):
        return "pending"
    return "passed"


def _blocking_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        check
        for check in checks
        if str(check["status"]).casefold() == "completed"
        and str(check["conclusion"]).casefold() not in _PASSING_CONCLUSIONS
    ]


def _pending_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [check for check in checks if str(check["status"]).casefold() != "completed"]


def _check_counts(checks: list[dict[str, Any]]) -> tuple[int, int]:
    return len(_blocking_checks(checks)), len(_pending_checks(checks))


def _mergeability(detail: dict[str, Any]) -> str:
    value = detail.get("mergeable")
    if value is True:
        return "mergeable"
    if value is False:
        return "conflicting"
    return "unknown"


def _pull_detail(repository: str, number: int) -> dict[str, Any]:
    return json.loads(_gh("api", f"repos/{repository}/pulls/{number}"))


def _open_pulls(repository: str) -> list[dict[str, Any]]:
    return _gh_paginated(
        f"repos/{repository}/pulls?state=open&per_page=100",
        ".[]",
    )


def _detailed_queue_entry(repository: str, pr: dict[str, Any]) -> dict[str, Any]:
    owner, _, name = repository.partition("/")
    # The list endpoint never carries mergeability: GitHub computes it
    # lazily and returns it only from the single-pull endpoint.
    detail = _pull_detail(repository, pr["number"])
    checks = _checks(owner, name, pr["head"]["sha"])
    threads = review_threads(owner, name, pr["number"])
    blocking_count, pending_count = _check_counts(checks)
    return {
        "repository": repository,
        "pr": pr["number"],
        "title": pr["title"],
        "base": pr["base"]["ref"],
        "head_branch": pr["head"]["ref"],
        "head_oid": pr["head"]["sha"],
        "draft": pr["draft"],
        "mergeability": _mergeability(detail),
        "mergeable_state": detail.get("mergeable_state"),
        "checks_verdict": checks_verdict(checks),
        "check_count": len(checks),
        "blocking_check_count": blocking_count,
        "pending_check_count": pending_count,
        "unresolved_threads": sum(1 for thread in threads if not thread["resolved"]),
    }


def cmd_locate(repository: str, number: int) -> dict[str, Any]:
    owner, _, name = repository.partition("/")
    pr = _pull_detail(repository, number)
    head_oid = pr["head"]["sha"]
    checks = _checks(owner, name, head_oid)
    threads = review_threads(owner, name, number)
    unresolved = [thread for thread in threads if not thread["resolved"]]
    return {
        "repository": repository,
        "pr": number,
        "title": pr["title"],
        "state": pr["state"],
        "draft": pr["draft"],
        "base": pr["base"]["ref"],
        "head_branch": pr["head"]["ref"],
        "head_oid": head_oid,
        "mergeability": _mergeability(pr),
        "mergeable_state": pr.get("mergeable_state"),
        "checks_verdict": checks_verdict(checks),
        "check_count": len(checks),
        "blocking_checks": _blocking_checks(checks),
        "pending_checks": _pending_checks(checks),
        "unresolved_threads": unresolved,
        "resolved_thread_count": len(threads) - len(unresolved),
    }


def landing_blockers(
    inventory: dict[str, Any], expected_base: str, expected_head: str
) -> list[str]:
    """Return every condition that prevents the inventoried PR from landing."""

    blockers: list[str] = []
    if inventory["base"] != expected_base:
        blockers.append(
            f"base is {inventory['base']}, expected authorized base {expected_base}"
        )
    if inventory["head_oid"] != expected_head:
        blockers.append(
            f"head_oid is {inventory['head_oid']}, expected authorized head {expected_head}"
        )
    if inventory["state"] != "open":
        blockers.append(f"state is {inventory['state']}, not open")
    if inventory["draft"]:
        blockers.append("pull request is a draft")
    if inventory["mergeability"] != "mergeable":
        blockers.append(f"mergeability is {inventory['mergeability']}")
    if inventory["mergeable_state"] != "clean":
        blockers.append(f"mergeable_state is {inventory['mergeable_state']}")
    if inventory["checks_verdict"] != "passed":
        blockers.append(f"checks_verdict is {inventory['checks_verdict']}")
    if inventory["unresolved_threads"]:
        blockers.append(
            f"{len(inventory['unresolved_threads'])} review thread(s) unresolved"
        )
    return blockers


def cmd_sweep(repositories: list[str], bases: set[str]) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for repository in repositories:
        for pr in _open_pulls(repository):
            if pr["base"]["ref"] in bases:
                queue.append(_detailed_queue_entry(repository, pr))
    return queue


def _body_text(arguments: argparse.Namespace) -> str:
    if arguments.body is not None:
        return arguments.body
    with open(arguments.body_file, encoding="utf-8") as handle:
        return handle.read()


def cmd_reply(thread_id: str, body: str) -> dict[str, Any]:
    mutation = """
    mutation($id:ID!,$body:String!){
      addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:$id,body:$body}){
        comment{databaseId}
      }
    }
    """
    data = _graphql(mutation, id=thread_id, body=body)
    return {"replied": data["addPullRequestReviewThreadReply"]["comment"]["databaseId"]}


def cmd_resolve(thread_id: str) -> dict[str, Any]:
    mutation = """
    mutation($id:ID!){
      resolveReviewThread(input:{threadId:$id}){thread{isResolved}}
    }
    """
    data = _graphql(mutation, id=thread_id)
    return {"resolved": data["resolveReviewThread"]["thread"]["isResolved"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    locate = sub.add_parser("locate", help="PR triage inventory as JSON")
    locate.add_argument("repository", help="owner/name")
    locate.add_argument("number", type=int)

    access = sub.add_parser("access", help="preflight one managed private repository")
    access.add_argument("repository", help="owner/name")
    access.add_argument("--effect", choices=tuple(_REQUIRED_PERMISSION), required=True)
    access.add_argument("--ssh-url")

    gate = sub.add_parser("gate", help="fail unless the PR is ready to land")
    gate.add_argument("repository", help="owner/name")
    gate.add_argument("number", type=int)
    gate.add_argument("--base", required=True, help="authorized integration branch")
    gate.add_argument("--head", required=True, help="authorized PR head OID")

    sweep = sub.add_parser("sweep", help="integration-lane PR queue as JSON")
    sweep.add_argument("repositories", nargs="+", help="owner/name list")
    sweep.add_argument(
        "--base",
        default="dev,develop,0.12.0-dev",
        help="comma-separated integration bases",
    )

    reply = sub.add_parser("reply", help="answer one review thread")
    reply.add_argument("thread_id")
    reply.add_argument("--body")
    reply.add_argument("--body-file")

    resolve = sub.add_parser("resolve", help="resolve one review thread")
    resolve.add_argument("thread_id")

    settle = sub.add_parser("settle", help="reply then resolve")
    settle.add_argument("thread_id")
    settle.add_argument("--body")
    settle.add_argument("--body-file")

    arguments = parser.parse_args()
    gate_blocked = False
    if arguments.command == "locate":
        result: Any = cmd_locate(arguments.repository, arguments.number)
    elif arguments.command == "access":
        result = managed_private_access(
            arguments.repository, arguments.effect, arguments.ssh_url
        )
    elif arguments.command == "gate":
        result = cmd_locate(arguments.repository, arguments.number)
        result["landing_blockers"] = landing_blockers(
            result, arguments.base, arguments.head
        )
        result["landing_verdict"] = (
            "blocked" if result["landing_blockers"] else "passed"
        )
        gate_blocked = bool(result["landing_blockers"])
    elif arguments.command == "sweep":
        result = cmd_sweep(arguments.repositories, set(arguments.base.split(",")))
    elif arguments.command == "reply":
        result = cmd_reply(arguments.thread_id, _body_text(arguments))
    elif arguments.command == "resolve":
        result = cmd_resolve(arguments.thread_id)
    elif arguments.command == "settle":
        body = _body_text(arguments)
        replied = cmd_reply(arguments.thread_id, body)
        resolved = cmd_resolve(arguments.thread_id)
        result = {**replied, **resolved}
    else:  # argparse guarantees one of the above
        raise SystemExit(f"unreachable command: {arguments.command}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if gate_blocked:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
