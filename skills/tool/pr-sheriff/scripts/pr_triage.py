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
  locate <owner/repo> <pr>            full PR triage inventory (JSON)
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


def _gh(*arguments: str, input_text: str | None = None) -> str:
    """Run gh in the operator's shell; propagate failure unchanged."""
    completed = subprocess.run(
        ["gh", *arguments],
        input=input_text,
        capture_output=True,
        text=True,
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
    raw = _gh(
        "api",
        f"repos/{owner}/{name}/commits/{ref}/check-runs",
        "-q",
        ".check_runs[] | {name:.name,status:.status,conclusion:.conclusion}",
    )
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def cmd_locate(repository: str, number: int) -> dict[str, Any]:
    owner, _, name = repository.partition("/")
    raw = _gh(
        "api",
        f"repos/{repository}/pulls/{number}",
    )
    pr = json.loads(raw)
    head_oid = pr["head"]["sha"]
    checks = _checks(owner, name, head_oid)
    threads = review_threads(owner, name, number)
    unresolved = [t for t in threads if not t["resolved"]]
    return {
        "repository": repository,
        "pr": number,
        "title": pr["title"],
        "state": pr["state"],
        "draft": pr["draft"],
        "base": pr["base"]["ref"],
        "head_branch": pr["head"]["ref"],
        "head_oid": head_oid,
        "mergeable": pr["mergeable"],
        "failing_checks": [c for c in checks if c["conclusion"] == "failure"],
        "pending_checks": [c for c in checks if c["status"] not in {"COMPLETED"}],
        "unresolved_threads": unresolved,
        "resolved_thread_count": len(threads) - len(unresolved),
    }


def cmd_sweep(repositories: list[str], bases: set[str]) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for repository in repositories:
        raw = _gh("api", f"repos/{repository}/pulls?state=open&per_page=100")
        pulls = json.loads(raw)
        for pr in pulls:
            if pr["base"]["ref"] not in bases:
                continue
            owner, _, name = repository.partition("/")
            checks = _checks(owner, name, pr["head"]["sha"])
            threads = review_threads(owner, name, pr["number"])
            queue.append(
                {
                    "repository": repository,
                    "pr": pr["number"],
                    "title": pr["title"],
                    "base": pr["base"]["ref"],
                    "head_branch": pr["head"]["ref"],
                    "head_oid": pr["head"]["sha"],
                    "draft": pr["draft"],
                    "mergeable": pr["mergeable_state"],
                    "failing_checks": sum(
                        1 for c in checks if c["conclusion"] == "failure"
                    ),
                    "pending_checks": sum(
                        1 for c in checks if c["status"] not in {"COMPLETED"}
                    ),
                    "unresolved_threads": sum(
                        1 for t in threads if not t["resolved"]
                    ),
                }
            )
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
        result = cmd_sweep(
            arguments.repositories, set(arguments.base.split(","))
        )
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
