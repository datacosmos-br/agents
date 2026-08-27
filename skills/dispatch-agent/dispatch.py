#!/usr/bin/env python3
"""Recommend an agent for a given task description."""
from __future__ import annotations

import json
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().with_name("agents.json")


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())["agents"]


def score(agent: dict, task: str) -> int:
    task_lower = task.lower()
    return sum(1 for trigger in agent.get("triggers", []) if trigger.lower() in task_lower)


def recommend(task: str) -> dict:
    agents = load_manifest()
    ranked = sorted(
        ((name, data, score(data, task)) for name, data in agents.items()),
        key=lambda x: x[2],
        reverse=True,
    )
    best_name, best_data, best_score = ranked[0]
    return {
        "task": task,
        "recommended_agent": best_name,
        "confidence": best_score,
        "alternatives": [
            {"name": name, "role": data["role"], "score": s}
            for name, data, s in ranked[1:4]
        ],
        "prompt": (
            f"You are now acting as the agent '{best_name}' ({best_data['role']}).\n"
            f"Model preference: {best_data.get('model', 'default')}\n"
            f"Summary: {best_data['summary']}\n\n"
            f"Task: {task}\n\n"
            "Execute this task through the active client's native agent interface."
        ),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: dispatch.py '<task description>'", file=sys.stderr)
        return 1
    task = " ".join(sys.argv[1:])
    print(json.dumps(recommend(task), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
