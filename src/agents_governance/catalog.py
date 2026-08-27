"""Typed catalog discovery and deterministic skill inventory."""

from __future__ import annotations

import fnmatch
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillPolicy:
    """Resolved policy for one canonical skill."""

    name: str
    class_name: str
    provenance: str
    updates: str
    max_tokens: int
    max_lines: int
    distributions: tuple[str, ...]


class Catalog:
    """Load authored policy and resolve it over the live skill tree."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.config = self._load_json(self.root / "config" / "skills.json")

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise TypeError(f"expected JSON object: {path}")
        return loaded

    def skill_dirs(self) -> tuple[Path, ...]:
        skills = self.root / "skills"
        return tuple(
            path
            for path in sorted(skills.iterdir())
            if not path.name.startswith(".") and (path / "SKILL.md").is_file()
        )

    def policy(self, name: str) -> SkillPolicy:
        selected = dict(self.config["default"])
        for rule in self.config["classification"]:
            if fnmatch.fnmatchcase(name, rule["pattern"]):
                selected.update(rule)
                break
        budgets = self.config["budgets"]
        if selected["updates"] == "forbidden":
            max_tokens = budgets["frozen_tokens"]
        elif selected["class"] == "router":
            max_tokens = budgets["router_tokens"]
        else:
            max_tokens = budgets["on_demand_tokens"]
        technologies = tuple(
            technology
            for technology, profile in self.config.get("technologies", {}).items()
            if name in profile["skills"]
        )
        distributions: tuple[str, ...]
        if selected["updates"] == "forbidden":
            distributions = ()
        elif technologies:
            distributions = tuple(f"technology:{item}" for item in technologies)
        elif name in self.config.get("project_generic", []):
            distributions = ("personal", "project-generic")
        else:
            distributions = ("personal",)
        return SkillPolicy(
            name=name,
            class_name=selected["class"],
            provenance=selected["provenance"],
            updates=selected["updates"],
            max_tokens=max_tokens,
            max_lines=budgets["max_lines"],
            distributions=distributions,
        )

    def names_for(self, distribution: str) -> frozenset[str]:
        """Return the explicit, fail-closed catalog selection for one surface."""

        return frozenset(
            directory.name
            for directory in self.skill_dirs()
            if distribution in self.policy(directory.name).distributions
        )

    def technology_profiles(self) -> dict[str, dict[str, Any]]:
        """Return the authored technology detection and skill profiles."""

        return dict(self.config.get("technologies", {}))

    @staticmethod
    def digest_tree(directory: Path) -> str:
        digest = hashlib.sha256()
        paths = (
            (directory,)
            if directory.is_file()
            else tuple(sorted(item for item in directory.rglob("*") if item.is_file()))
        )
        for path in paths:
            relative = (
                path.name
                if directory.is_file()
                else path.relative_to(directory).as_posix()
            )
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def inventory(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for directory in self.skill_dirs():
            policy = self.policy(directory.name)
            entries.append(
                {
                    "name": directory.name,
                    "owner": "agents",
                    "class": policy.class_name,
                    "provenance": policy.provenance,
                    "updates": policy.updates,
                    "max_tokens": policy.max_tokens,
                    "max_lines": policy.max_lines,
                    "distributions": list(policy.distributions),
                    "digest": self.digest_tree(directory),
                }
            )
        return entries
