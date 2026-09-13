"""Normalize evaluation YAML EOFs after structural codemods."""

from __future__ import annotations

import os
from pathlib import Path

_MODES = frozenset({"apply", "check"})


def main() -> None:
    mode = os.environ.get("EVAL_YAML_MODE", "apply")
    if mode not in _MODES:
        raise ValueError("EVAL_YAML_MODE must equal apply or check")
    repository = Path(__file__).resolve().parents[1]
    eval_root = repository / "evals"
    for path in sorted(eval_root.rglob("*.yaml")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"evaluation YAML must be a physical file: {path}")
        source = path.read_text(encoding="utf-8")
        normalized = f"{source.strip()}\n"
        if source == normalized:
            continue
        if mode == "check":
            relative = path.relative_to(repository)
            raise ValueError(f"evaluation YAML is not normalized: {relative}")
        path.write_text(normalized, encoding="utf-8")


if __name__ == "__main__":
    main()
