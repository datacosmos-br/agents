"""Validate the configured Waza development runtime against its live catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

import yaml


def _mapping(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{context} must be a mapping with string keys")
    return cast(dict[str, object], value)


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    config = _mapping(
        yaml.safe_load((repository / ".waza.yaml").read_text(encoding="utf-8")),
        ".waza.yaml",
    )
    defaults = _mapping(config.get("defaults"), ".waza.yaml defaults")
    if defaults.get("engine") != "copilot-sdk":
        raise ValueError("Waza development runtime must use the real copilot-sdk")
    model = defaults.get("model")
    if not isinstance(model, str) or not model.strip() or model == "auto":
        raise ValueError("Waza development runtime must name one concrete model")

    catalog = json.load(sys.stdin)
    if not isinstance(catalog, list):
        raise TypeError("Waza model catalog must be a list")
    matches = [
        _mapping(item, "Waza model catalog item")
        for item in catalog
        if isinstance(item, dict) and item.get("id") == model
    ]
    if len(matches) != 1:
        raise ValueError(f"configured Waza model is not present exactly once: {model}")
    policy = _mapping(matches[0].get("policy"), f"Waza model {model} policy")
    if policy.get("state") != "enabled":
        raise ValueError(f"configured Waza model is not enabled: {model}")
    print(f"Waza runtime: copilot-sdk / {model} (enabled)")


if __name__ == "__main__":
    main()
