"""Strict semantic discovery and deterministic skill inventory."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast

from .approvals import APPROVAL_NAMESPACES, resolve_approval_tags
from .frontmatter import cast_mapping, parse_frontmatter, require_exact_fields

NON_PORTABLE_PROJECT_REFERENCE = re.compile(
    r"(?:"
    r"~[/\\]"
    r"|\$(?:HOME\b|\{HOME\})"
    r"|(?<![A-Za-z0-9._/-])/(?:home/[^/\s`'\"()]+|Users/[^/\s`'\"()]+|root)(?:[/\\]|\b)"
    r"|(?i:[A-Z]:\\Users\\[^\\\s`'\"()]+(?:\\|\b))"
    r"|(?i:file://)"
    r"|(?<![A-Za-z0-9_.-])\.(?:agents|beads|claude)(?:[/\\]|\b)"
    r"|(?i:\b(?:Gas[ -]?(?:Town|City)|AI[ -]Hub|Beads|Dolt)\b)"
    r")"
)

_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_TAG = re.compile(r"[a-z][a-z0-9-]*(?::[^\s,\[\]\"']+)+\Z")
_TAG_NAMESPACES = (
    frozenset(
        {
            "activation",
            "detect",
            "domain",
            "framework",
            "lens",
            "mode",
            "policy",
            "provenance",
            "role",
            "route",
            "technology",
            "tool",
            "updates",
            "usage",
        }
    )
    | APPROVAL_NAMESPACES
)
_USAGE_TAGS = frozenset({"usage:frozen", "usage:on-demand", "usage:router"})
_UPDATES_TAGS = frozenset({"updates:forbidden", "updates:manual"})
_ROUTE_TAGS = frozenset({"route:agent", "route:project"})
_ACTIVATION_TAGS = frozenset(
    {"activation:detected", "activation:detected-or-opt-in", "activation:opt-in"}
)
_POLICY_TAGS = frozenset(
    {
        "policy:atomic-effects",
        "policy:causal-subprocess",
        "policy:fail-loud",
        "policy:no-fallback",
        "policy:no-keyring",
        "policy:preflight-before-effects",
        "policy:required-environment",
        "policy:strict-execution",
        "policy:zero-residue",
    }
)
_FRONTMATTER_FIELDS = frozenset(
    {"allowed-tools", "compatibility", "description", "license", "metadata", "name"}
)
_OPTIONAL_STRING_FIELDS = frozenset({"allowed-tools", "compatibility", "license"})
_BUDGET_FIELDS = frozenset(
    {"router_tokens", "frozen_tokens", "on_demand_tokens", "max_lines"}
)


class SkillCategory(StrEnum):
    """The path-owned primary semantic category of a skill."""

    AGENT_WIDE = "agent-wide"
    PROJECT_WIDE = "project-wide"
    TECHNOLOGY = "technology"
    FRAMEWORK = "framework"
    TOOL = "tool"
    DOMAIN = "domain"

    @property
    def conditional(self) -> bool:
        return self not in {self.AGENT_WIDE, self.PROJECT_WIDE}


@dataclass(frozen=True)
class SkillRecord:
    """One fully validated canonical skill source."""

    name: str
    category: SkillCategory
    directory: Path
    tags: tuple[str, ...]
    usage: str
    updates: str
    provenance: str
    routes: tuple[str, ...]
    activation: str | None
    subjects: tuple[str, ...]
    detectors: tuple[str, ...]


class Catalog:
    """Discover and validate every canonical skill before returning any record."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=True)
        self._load_policy(self.root / "config" / "skills.json")
        self._records = self._discover()
        for record in self._records:
            resolve_approval_tags(self.root, record.tags, record.directory / "SKILL.md")

    @staticmethod
    def _load_policy(path: Path) -> dict[str, object]:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"skills policy must be a physical file: {path}")
        loaded = cast_mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
        require_exact_fields(loaded, frozenset({"version", "budgets"}), str(path))
        if loaded["version"] != 2:
            raise ValueError(f"skills policy version must be 2: {path}")
        budgets = cast_mapping(loaded["budgets"], f"{path}: budgets")
        require_exact_fields(budgets, _BUDGET_FIELDS, f"{path}: budgets")
        for key in sorted(_BUDGET_FIELDS):
            value = budgets[key]
            if type(value) is not int or value <= 0:
                raise TypeError(f"budgets.{key} must be a positive integer: {path}")
        return loaded

    @staticmethod
    def _frontmatter(path: Path) -> dict[str, object]:
        frontmatter, _ = parse_frontmatter(path)
        unknown = frozenset(frontmatter) - _FRONTMATTER_FIELDS
        if unknown:
            raise ValueError(
                f"{path}: unsupported skill frontmatter fields: "
                + ", ".join(sorted(unknown))
            )
        for field in sorted(_OPTIONAL_STRING_FIELDS):
            if field not in frontmatter:
                continue
            value = frontmatter[field]
            if not isinstance(value, str) or not value or value != value.strip():
                raise TypeError(f"{path}: {field} must be a non-empty trimmed string")
        return frontmatter

    @staticmethod
    def _one_tag(
        path: Path, tags: tuple[str, ...], prefix: str, allowed: frozenset[str]
    ) -> str:
        selected = tuple(tag for tag in tags if tag.startswith(f"{prefix}:"))
        if len(selected) != 1:
            raise ValueError(
                f"{path}: expected exactly one {prefix}:* tag; got {len(selected)}"
            )
        if selected[0] not in allowed:
            raise ValueError(f"{path}: unsupported tag: {selected[0]}")
        return selected[0].split(":", 1)[1]

    @staticmethod
    def _validate_detector(path: Path, tag: str) -> None:
        parts = tag.split(":", 3)
        if len(parts) < 3:
            raise ValueError(f"{path}: invalid detector tag: {tag}")
        kind = parts[1]
        value = ":".join(parts[2:])
        if kind == "marker":
            marker = PurePosixPath(value)
            if (
                marker.is_absolute()
                or marker == PurePosixPath(".")
                or ".." in marker.parts
            ):
                raise ValueError(f"{path}: detector marker escapes project: {tag}")
            return
        if kind == "dependency":
            if len(parts) != 4 or not parts[2] or not parts[3]:
                raise ValueError(
                    f"{path}: dependency detector requires ecosystem and name: {tag}"
                )
            return
        if kind == "owned-extension":
            if "/" in value or not value.startswith(".") or value in {".", ".."}:
                raise ValueError(f"{path}: invalid owned extension detector: {tag}")
            return
        if kind not in {"owned-glob", "opt-in", "selected-tag"} or not value:
            raise ValueError(f"{path}: unsupported detector tag: {tag}")

    def _record(
        self, skill_file: Path, category: SkillCategory, slug: str
    ) -> SkillRecord:
        frontmatter = self._frontmatter(skill_file)
        if "name" not in frontmatter:
            raise ValueError(f"{skill_file}: name is required")
        name = frontmatter["name"]
        if not isinstance(name, str) or _NAME.fullmatch(name) is None:
            raise ValueError(f"{skill_file}: invalid name")
        if name != slug:
            raise ValueError(f"{skill_file}: declared name {name!r} != {slug!r}")
        if "metadata" not in frontmatter:
            raise ValueError(f"{skill_file}: metadata is required")
        metadata = cast_mapping(frontmatter["metadata"], f"{skill_file}: metadata")
        if "aihub.tags" not in metadata:
            raise ValueError(f"{skill_file}: metadata.aihub.tags is required")
        raw_tags = metadata["aihub.tags"]
        if not isinstance(raw_tags, str):
            raise TypeError(f"{skill_file}: metadata.aihub.tags must be a JSON string")
        decoded = json.loads(raw_tags)
        if not isinstance(decoded, list) or not all(
            isinstance(item, str) for item in decoded
        ):
            raise TypeError(f"{skill_file}: metadata.aihub.tags must encode strings")
        tags = tuple(cast(list[str], decoded))
        if len(tags) != len(set(tags)):
            raise ValueError(f"{skill_file}: tags must be unique")
        if tags != tuple(sorted(tags)):
            raise ValueError(f"{skill_file}: tags must be sorted")
        for tag in tags:
            if _TAG.fullmatch(tag) is None:
                raise ValueError(f"{skill_file}: invalid tag: {tag}")
            if tag.split(":", 1)[0] not in _TAG_NAMESPACES:
                raise ValueError(f"{skill_file}: unsupported tag namespace: {tag}")
            if tag.startswith("policy:") and tag not in _POLICY_TAGS:
                raise ValueError(f"{skill_file}: unsupported tag: {tag}")

        usage = self._one_tag(skill_file, tags, "usage", _USAGE_TAGS)
        updates = self._one_tag(skill_file, tags, "updates", _UPDATES_TAGS)
        provenance_tags = tuple(tag for tag in tags if tag.startswith("provenance:"))
        if len(provenance_tags) != 1:
            raise ValueError(
                f"{skill_file}: expected exactly one provenance:* tag; "
                f"got {len(provenance_tags)}"
            )
        provenance = provenance_tags[0].split(":", 1)[1]
        if (usage == "frozen") != (updates == "forbidden"):
            raise ValueError(
                f"{skill_file}: usage:frozen and updates:forbidden must coexist"
            )

        route_tags = tuple(tag for tag in tags if tag.startswith("route:"))
        activation_tags = tuple(tag for tag in tags if tag.startswith("activation:"))
        detectors = tuple(tag for tag in tags if tag.startswith("detect:"))
        subjects = tuple(
            tag.split(":", 1)[1] for tag in tags if tag.startswith(f"{category.value}:")
        )
        routes: tuple[str, ...] = ()
        activation: str | None = None
        if category.conditional:
            if not route_tags or any(tag not in _ROUTE_TAGS for tag in route_tags):
                raise ValueError(
                    f"{skill_file}: conditional skill requires at least one of "
                    f"{', '.join(sorted(_ROUTE_TAGS))}; got "
                    f"{', '.join(route_tags) or 'none'}"
                )
            routes = tuple(tag.split(":", 1)[1] for tag in route_tags)
            activation = self._one_tag(skill_file, tags, "activation", _ACTIVATION_TAGS)
            if not subjects:
                raise ValueError(
                    f"{skill_file}: {category.value}:* category tag is required"
                )
            requires_runtime = activation in {"detected", "detected-or-opt-in"}
            if requires_runtime and not any(
                not tag.startswith("detect:opt-in:") for tag in detectors
            ):
                raise ValueError(
                    f"{skill_file}: activation:{activation} requires runtime detector"
                )
            if activation in {"opt-in", "detected-or-opt-in"} and not any(
                tag.startswith("detect:opt-in:") for tag in detectors
            ):
                raise ValueError(
                    f"{skill_file}: activation:{activation} requires opt-in detector"
                )
            for detector in detectors:
                self._validate_detector(skill_file, detector)
        elif route_tags or activation_tags or detectors:
            raise ValueError(
                f"{skill_file}: {category.value} distribution is path-owned"
            )

        return SkillRecord(
            slug,
            category,
            skill_file.parent,
            tags,
            usage,
            updates,
            provenance,
            routes,
            activation,
            subjects,
            detectors,
        )

    def _discover(self) -> tuple[SkillRecord, ...]:
        skills_root = self.root / "skills"
        if skills_root.is_symlink() or not skills_root.is_dir():
            raise ValueError(f"skills root must be a physical directory: {skills_root}")
        skill_files = tuple(sorted(skills_root.rglob("SKILL.md")))
        if not skill_files:
            raise ValueError(f"skill inventory is empty: {skills_root}")
        records: list[SkillRecord] = []
        names: set[str] = set()
        for skill_file in skill_files:
            relative = skill_file.relative_to(skills_root)
            if len(relative.parts) not in (3, 4):
                raise ValueError(
                    f"{skill_file}: skill path must be <category>/<slug>/SKILL.md or <category>/<subcategory>/<slug>/SKILL.md"
                )
            if len(relative.parts) == 3:
                raw_category, slug, filename = relative.parts
            else:
                raw_category, _subcategory, slug, filename = relative.parts
            if filename != "SKILL.md" or skill_file.is_symlink():
                raise ValueError(
                    f"{skill_file}: skill source must be physical SKILL.md"
                )
            category = SkillCategory(raw_category)
            record = self._record(skill_file, category, slug)
            if record.name in names:
                raise ValueError(f"{skill_file}: duplicate skill name: {record.name}")
            names.add(record.name)
            records.append(record)
        return tuple(sorted(records, key=lambda record: record.name))

    def records(self) -> tuple[SkillRecord, ...]:
        return self._records

__all__ = (
    "NON_PORTABLE_PROJECT_REFERENCE",
    "Catalog",
    "SkillCategory",
    "SkillRecord",
)
