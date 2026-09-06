#!/usr/bin/env python3
"""Locate, reply to, and resolve pull-request review comments via gh.

Companion tooling for the pr-sheriff skill. Read-only subcommands
(`locate`, `sweep`) are preflight evidence; `reply`, `resolve`, and
`settle` perform the single named GitHub effect and nothing else.

Strict-execution contract: the first gh or GraphQL failure escapes with
its stderr and a nonzero exit; there is no fallback, retry, credential
handling, or success claim without the effect's own confirmation.
Dependencies: python3 stdlib and the `gh` CLI already authenticated by
the operator's shell. Never extracts or relocates credentials.

Subcommands:
  locate <owner/repo> <pr>            full blocking-check inventory (JSON)
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
        raise SystemExit(
            f"gh {' '.join(arguments[:2])}... exited {completed.returncode}"
        )
    return completed.stdout


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
        if check["status"] == "COMPLETED"
        and str(check["conclusion"]).casefold() not in _PASSING_CONCLUSIONS
    ]


def _pending_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [check for check in checks if check["status"] != "COMPLETED"]


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
    if arguments.command == "locate":
        result: Any = cmd_locate(arguments.repository, arguments.number)
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


if __name__ == "__main__":
    main()
