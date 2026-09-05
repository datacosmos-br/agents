"""Normalize evaluation YAML EOFs after structural codemods."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    eval_root = repository / "evals"
    for path in sorted(eval_root.rglob("*.yaml")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"evaluation YAML must be a physical file: {path}")
        source = path.read_text(encoding="utf-8")
        normalized = f"{source.rstrip()}\n"
        if source != normalized:
            path.write_text(normalized, encoding="utf-8")


if __name__ == "__main__":
    main()
