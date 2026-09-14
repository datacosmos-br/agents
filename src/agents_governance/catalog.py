"""Strict semantic discovery and deterministic skill inventory."""

from __future__ import annotations

import json
import re
import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast

from .approvals import APPROVAL_NAMESPACES, resolve_approval_tags
from .frontmatter import cast_mapping, parse_frontmatter, require_exact_fields
from .markdown_references import local_reference_targets, resolve_physical_reference
from .skill_resources import ResourcePolicy, SkillResource

NON_PORTABLE_PROJECT_REFERENCE = re.compile(
    r"(?:"
    r"~[/\\]"
    r"|\$(?:HOME\b|\{HOME\})"
    r"|(?<![A-Za-z0-9._/-])/(?:home/[^/\s`'\"()]+|Users/[^/\s`'\"()]+|root)(?:[/\\]|\b)"
    r"|(?i:[A-Z]:\\Users\\[^\\\s`'\"()]+(?:\\|\b))"
    r"|(?i:file:///)"
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
            "extends",
            "route",
            "subject",
            "usage",
        }
    )
    | APPROVAL_NAMESPACES
)
_USAGE_TAGS = frozenset({"usage:frozen", "usage:on-demand", "usage:router"})
_ROUTE_TAGS = frozenset({"route:agent", "route:project"})
_ACTIVATION_TAGS = frozenset(
    {"activation:detected", "activation:detected-or-opt-in", "activation:opt-in"}
)
_SUBJECTS = frozenset(
    {
        "agent-browser",
        "agents",
        "architecture",
        "argocd",
        "beads",
        "bun",
        "context7",
        "cosmos-gitops",
        "cpp",
        "dart",
        "deployment",
        "dmux",
        "dry",
        "exa",
        "fal-ai",
        "flext",
        "flutter",
        "frontend",
        "fundraising",
        "gascity",
        "git",
        "github",
        "go",
        "helm",
        "jvm",
        "language",
        "market-research",
        "mcp",
        "mle",
        "nextjs",
        "openspec",
        "playwright",
        "pydantic",
        "python",
        "react",
        "rust",
        "schema",
        "scope",
        "ts",
        "turbopack",
        "upstream",
        "vault",
        "video",
        "web",
        "x-api",
    }
)
_FRONTMATTER_FIELDS = frozenset(
    {"allowed-tools", "compatibility", "description", "license", "metadata", "name"}
)
_OPTIONAL_STRING_FIELDS = frozenset({"allowed-tools", "compatibility", "license"})
_BUDGET_FIELDS = frozenset(
    {"router_tokens", "frozen_tokens", "on_demand_tokens", "max_lines"}
)
_DESCRIPTION_TOKEN = r"[a-z0-9](?:[a-z0-9+./_-]*[a-z0-9+])?"
_DESCRIPTION_TERM = re.compile(
    rf"{_DESCRIPTION_TOKEN}(?: {_DESCRIPTION_TOKEN}){{0,2}}\Z"
)
_PROSE_MARKERS = frozenset(
    {
        "after",
        "because",
        "before",
        "during",
        "if",
        "then",
        "that",
        "when",
        "where",
        "which",
        "while",
        "whose",
    }
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
    description: str
    tags: tuple[str, ...]
    usage: str
    routes: tuple[str, ...]
    activation: str | None
    subjects: tuple[str, ...]
    detectors: tuple[str, ...]
    parents: tuple[str, ...]
    resources: tuple[SkillResource, ...]


class Catalog:
    """Discover and validate every canonical skill before returning any record."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=True)
        self._policy = self._load_policy(self.root / "config" / "skills.json")
        self._resource_policy = ResourcePolicy.parse(self._policy["resources"])
        self._records = self._discover()
        self._resource_policy.validate_inventory(
            self.root,
            tuple(
                resource for record in self._records for resource in record.resources
            ),
        )
        self._validate_hierarchy()
        self._validate_tree()
        for record in self._records:
            resolve_approval_tags(self.root, record.tags, record.directory / "SKILL.md")

    @staticmethod
    def _load_policy(path: Path) -> dict[str, object]:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"skills policy must be a physical file: {path}")
        loaded = cast_mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
        require_exact_fields(
            loaded, frozenset({"version", "budgets", "resources"}), str(path)
        )
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
    def _require_description(value: object, path: Path) -> None:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{path}: description is required")
        if value != value.strip() or "\n" in value or "\r" in value:
            raise ValueError(f"{path}: description must be one trimmed line")
        if not 12 <= len(value) <= 96 or value != value.casefold():
            raise ValueError(f"{path}: description must be 12-96 lowercase characters")
        if re.search(r",(?! )| ,", value):
            raise ValueError(f"{path}: description terms require comma-space")
        terms = value.split(", ")
        if not 3 <= len(terms) <= 10 or len(terms) != len(set(terms)):
            raise ValueError(f"{path}: description requires 3-10 unique terms")
        if any(marker in term.split() for term in terms for marker in _PROSE_MARKERS):
            raise ValueError(f"{path}: description must be terms, not prose")
        if any(_DESCRIPTION_TERM.fullmatch(term) is None for term in terms):
            raise ValueError(f"{path}: description contains an invalid term")

    @staticmethod
    def _physical_tree(directory: Path) -> tuple[Path, ...]:
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"skill bundle must be a physical directory: {directory}")
        paths = tuple(sorted(directory.rglob("*")))
        for path in paths:
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink forbidden in skill bundle: {path}")
            if not stat.S_ISDIR(mode) and not stat.S_ISREG(mode):
                raise ValueError(f"unsupported skill resource type: {path}")
        return paths

    def _require_local_links(self, directory: Path, markdown: Path) -> None:
        text = markdown.read_text(encoding="utf-8")
        for target in local_reference_targets(markdown, text):
            resolved = resolve_physical_reference(directory, markdown, target)
            resolved.relative_to(self.root)

    def _validate_record(self, record: SkillRecord) -> None:
        directory = record.directory
        skill_file = directory / "SKILL.md"
        frontmatter = self._frontmatter(skill_file)
        self._require_description(frontmatter.get("description"), skill_file)
        budgets = cast(dict[str, int], self._policy["budgets"])
        if (
            len(skill_file.read_text(encoding="utf-8").splitlines())
            > budgets["max_lines"]
        ):
            raise ValueError(f"{skill_file}: skill exceeds max_lines")
        project_distributed = record.category is SkillCategory.PROJECT_WIDE or (
            record.category.conditional
            and "project" in record.routes
            and record.activation != "opt-in"
        )
        textual = (
            skill_file,
            *(
                resource.path
                for resource in record.resources
                if resource.format == "utf-8"
            ),
        )
        for path in textual:
            text = path.read_text(encoding="utf-8")
            if project_distributed and NON_PORTABLE_PROJECT_REFERENCE.search(text):
                raise ValueError(f"project-distributed skill is not portable: {path}")
            if path.suffix == ".md":
                self._require_local_links(directory, path)

    def _validate_tree(self) -> None:
        skills_root = self.root / "skills"
        allowed_root_files = {skills_root / "README.md"}
        category_roots = {skills_root / category.value for category in SkillCategory}
        for entry in skills_root.iterdir():
            if entry in allowed_root_files:
                if entry.is_symlink() or not entry.is_file():
                    raise ValueError(f"skill root document must be physical: {entry}")
                continue
            if entry not in category_roots:
                raise ValueError(f"unknown skill root entry: {entry}")
        # Owner lookup is a set, not a scan. Membership was
        # `any(resolved.is_relative_to(owner) for owner in owners)`, which is
        # O(files x owners) of an expensive path comparison; on this bundle it
        # was 22_783 calls and about 6.9s of the load. Walking the resolved
        # path's own parents is O(depth) of hash lookups instead.
        owners = frozenset(
            record.directory.resolve(strict=True) for record in self._records
        )
        for category_root in sorted(category_roots):
            if category_root.is_symlink() or not category_root.is_dir():
                raise ValueError(f"skill category must be physical: {category_root}")
            for path in sorted(category_root.rglob("*")):
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode):
                    raise ValueError(f"symlink forbidden in skills tree: {path}")
                if stat.S_ISDIR(mode):
                    if not any(path.iterdir()):
                        raise ValueError(f"empty skill directory is forbidden: {path}")
                    continue
                if not stat.S_ISREG(mode):
                    raise ValueError(f"unsupported skill resource type: {path}")
                resolved = path.resolve(strict=True)
                if resolved not in owners and not any(
                    parent in owners for parent in resolved.parents
                ):
                    raise ValueError(
                        f"orphan skill resource has no SKILL.md owner: {path}"
                    )
        for record in self._records:
            self._validate_record(record)

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

        usage = self._one_tag(skill_file, tags, "usage", _USAGE_TAGS)

        route_tags = tuple(tag for tag in tags if tag.startswith("route:"))
        activation_tags = tuple(tag for tag in tags if tag.startswith("activation:"))
        detectors = tuple(tag for tag in tags if tag.startswith("detect:"))
        parents = tuple(
            tag.split(":", 1)[1] for tag in tags if tag.startswith("extends:")
        )
        if any(_NAME.fullmatch(parent) is None for parent in parents):
            raise ValueError(f"{skill_file}: invalid extends:* skill name")
        if name in parents:
            raise ValueError(f"{skill_file}: a skill cannot extend itself")
        subjects = tuple(
            tag.split(":", 1)[1] for tag in tags if tag.startswith("subject:")
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
                    f"{skill_file}: conditional skill requires at least one "
                    f"subject:* tag"
                )
            unknown_subjects = frozenset(subjects) - _SUBJECTS
            if unknown_subjects:
                raise ValueError(
                    f"{skill_file}: unsupported subjects: "
                    + ", ".join(sorted(unknown_subjects))
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
        elif route_tags or activation_tags or detectors or subjects:
            raise ValueError(
                f"{skill_file}: {category.value} distribution is path-owned"
            )

        return SkillRecord(
            slug,
            category,
            skill_file.parent,
            cast(str, frontmatter["description"]),
            tags,
            usage,
            routes,
            activation,
            subjects,
            detectors,
            parents,
            tuple(
                self._resource_policy.resource(self.root, path)
                for path in self._physical_tree(skill_file.parent)
                if path.is_file() and path != skill_file
            ),
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

    def _validate_hierarchy(self) -> None:
        """Validate the explicit general-to-specialized skill dependency DAG."""
        by_name = {record.name: record for record in self._records}
        ranks = {
            SkillCategory.AGENT_WIDE: 0,
            SkillCategory.PROJECT_WIDE: 0,
            SkillCategory.TECHNOLOGY: 1,
            SkillCategory.FRAMEWORK: 2,
            SkillCategory.TOOL: 2,
            SkillCategory.DOMAIN: 2,
        }
        for record in self._records:
            router = (record.directory / "SKILL.md").read_text(encoding="utf-8")
            for parent_name in record.parents:
                parent = by_name.get(parent_name)
                if parent is None:
                    raise ValueError(
                        f"{record.directory / 'SKILL.md'}: unknown parent skill: {parent_name}"
                    )
                if ranks[parent.category] > ranks[record.category]:
                    raise ValueError(
                        f"{record.directory / 'SKILL.md'}: parent {parent_name!r} is "
                        "more specialized than its child"
                    )
                if f"${parent_name}" not in router:
                    raise ValueError(
                        f"{record.directory / 'SKILL.md'}: parent ${parent_name} must "
                        "be referenced explicitly"
                    )

        visited: set[str] = set()
        active: list[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return
            if name in active:
                start = active.index(name)
                cycle = " -> ".join((*active[start:], name))
                raise ValueError(f"cyclic skill hierarchy: {cycle}")
            active.append(name)
            for parent_name in by_name[name].parents:
                visit(parent_name)
            active.pop()
            visited.add(name)

        for name in sorted(by_name):
            visit(name)

    def records(self) -> tuple[SkillRecord, ...]:
        return self._records


__all__ = (
    "NON_PORTABLE_PROJECT_REFERENCE",
    "Catalog",
    "SkillCategory",
    "SkillRecord",
)
