#!/usr/bin/env python3
"""Step-by-step reasoning helper."""
from __future__ import annotations

import sys


def think(problem: str, steps: int = 5) -> str:
    lines = [f"Problem: {problem}", "Step-by-step reasoning:"]
    for i in range(1, steps + 1):
        lines.append(f"{i}. [analyze constraints and options]")
    lines.append("Conclusion: [synthesize best path forward]")
    return "\n".join(lines)


if __name__ == "__main__":
    problem = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Analyze the current task"
    print(think(problem))
