"""Typed semantic discovery and deterministic skill inventory."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any, cast

import yaml

NON_PORTABLE_PROJECT_REFERENCE = re.compile(
    r"(?:"
    r"~[/\\]"
    r"|\$(?:HOME\b|\{HOME\})"
    r"|(?<![A-Za-z0-9._/-])/(?:home/[^/\s`'\"()]+|Users/[^/\s`'\"()]+|root)(?:[/\\]|\b)"
    r"|(?i:[A-Z]:\\Users\\[^\\\s`'\"()]+(?:\\|\b))"
    r"|(?i:file://)"
    r"|(?<![A-Za-z0-9_.-])\.(?:agents|beads|claude)(?:[/\\]|\b)"
    r"|(?i:\b(?:Gas[ -]?(?:Town|City)|AI[ -]Hub|Beads|Dolt|FLEXT)\b)"
    r")"
)

_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_TAG = re.compile(r"^[a-z][a-z0-9-]*(?::[^\s,\[\]\"']+)+$")
_TAG_NAMESPACES = frozenset(
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
_USAGE_TAGS = frozenset({"usage:frozen", "usage:on-demand", "usage:router"})
_UPDATES_TAGS = frozenset({"updates:forbidden", "updates:manual"})
_ROUTE_TAGS = frozenset({"route:agent", "route:project"})
_ACTIVATION_TAGS = frozenset(
    {
        "activation:detected",
        "activation:detected-or-opt-in",
        "activation:opt-in",
    }
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
_SKILL_FRONTMATTER_FIELDS = frozenset(
    {
        "allowed-tools",
        "compatibility",
        "description",
        "license",
        "metadata",
        "name",
    }
)
_OPTIONAL_STRING_FIELDS = frozenset({"allowed-tools", "compatibility", "license"})
_INVENTORY_VERSION = 1


class SkillCategory(str, Enum):
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
class CatalogFinding:
    """One deterministic semantic catalog defect."""

    path: str
    code: str
    message: str


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
    route: str | None
    activation: str | None
    subjects: tuple[str, ...]
    detectors: tuple[str, ...]


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
    category: SkillCategory
    tags: tuple[str, ...]


class Catalog:
    """Discover skill contracts from canonical paths and local metadata."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.config = self._load_json(self.root / "config" / "skills.json")
        self._directories, self._records, self._findings = self._discover()

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise TypeError(f"expected JSON object: {path}")
        if set(loaded) != {"version", "budgets"}:
            unexpected = ", ".join(sorted(set(loaded) - {"version", "budgets"}))
            missing = ", ".join(sorted({"version", "budgets"} - set(loaded)))
            detail = unexpected or f"missing {missing}"
            raise ValueError(f"unsupported skills policy fields ({detail}): {path}")
        if loaded["version"] != 2:
            raise ValueError(f"skills policy version must be 2: {path}")
        budgets = loaded.get("budgets")
        if not isinstance(budgets, dict):
            raise TypeError(f"expected budgets object: {path}")
        required = {
            "router_tokens",
            "frozen_tokens",
            "on_demand_tokens",
            "max_lines",
        }
        if set(budgets) != required:
            unexpected = ", ".join(sorted(set(budgets) - required))
            missing = ", ".join(sorted(required - set(budgets)))
            detail = unexpected or f"missing {missing}"
            raise ValueError(f"unsupported skill budget fields ({detail}): {path}")
        for key in sorted(required):
            value = budgets.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise TypeError(f"budgets.{key} must be a positive integer: {path}")
        return loaded

    @staticmethod
    def _relative(root: Path, path: Path) -> str:
        return path.relative_to(root).as_posix()

    @staticmethod
    def _frontmatter(path: Path) -> dict[str, object]:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            raise ValueError("missing YAML frontmatter")
        marker = text.find("\n---\n", 4)
        if marker < 0:
            raise ValueError("unterminated YAML frontmatter")
        loaded = yaml.safe_load(text[4:marker])
        if not isinstance(loaded, dict):
            raise TypeError("frontmatter must be a mapping")
        raw = cast(dict[object, object], loaded)
        if not all(isinstance(key, str) for key in raw):
            raise TypeError("frontmatter keys must be strings")
        frontmatter = cast(dict[str, object], raw)
        unknown = sorted(set(frontmatter) - _SKILL_FRONTMATTER_FIELDS)
        if unknown:
            raise ValueError(
                "unsupported skill frontmatter fields: " + ", ".join(unknown)
            )
        for field in sorted(_OPTIONAL_STRING_FIELDS):
            value = frontmatter.get(field)
            if value is not None and (
                not isinstance(value, str)
                or not value.strip()
                or value != value.strip()
            ):
                raise TypeError(f"{field} must be a non-empty trimmed string")
        return frontmatter

    @staticmethod
    def _singleton(
        tags: tuple[str, ...], prefix: str, allowed: frozenset[str]
    ) -> tuple[str | None, list[tuple[str, str]]]:
        selected = tuple(tag for tag in tags if tag.startswith(f"{prefix}:"))
        errors: list[tuple[str, str]] = []
        if len(selected) != 1:
            errors.append(
                (
                    "tag-required",
                    f"expected exactly one {prefix}:* tag; got {len(selected)}",
                )
            )
            return None, errors
        if selected[0] not in allowed:
            errors.append(("tag-value", f"unsupported tag: {selected[0]}"))
            return None, errors
        return selected[0].split(":", 1)[1], errors

    @staticmethod
    def _detector_error(tag: str) -> str | None:
        parts = tag.split(":", 3)
        if len(parts) < 3:
            return f"invalid detector tag: {tag}"
        kind = parts[1]
        value = ":".join(parts[2:])
        if kind == "marker":
            marker = PurePosixPath(value)
            if (
                marker.is_absolute()
                or marker == PurePosixPath(".")
                or ".." in marker.parts
            ):
                return f"detector marker must remain inside a project: {tag}"
            return None
        if kind == "dependency":
            if len(parts) != 4 or not parts[2] or not parts[3]:
                return f"dependency detector requires ecosystem and name: {tag}"
            return None
        if kind == "owned-extension":
            if "/" in value or not value.startswith(".") or value in {".", ".."}:
                return f"invalid owned extension detector: {tag}"
            return None
        if kind in {"owned-glob", "opt-in", "selected-tag"} and value:
            return None
        return f"unsupported detector tag: {tag}"

    def _parse_record(
        self, skill_file: Path, category: SkillCategory, slug: str
    ) -> tuple[SkillRecord | None, list[CatalogFinding]]:
        relative = self._relative(self.root, skill_file)
        findings: list[CatalogFinding] = []
        try:
            frontmatter = self._frontmatter(skill_file)
        except (OSError, UnicodeError, TypeError, ValueError, yaml.YAMLError) as error:
            return None, [CatalogFinding(relative, "frontmatter", str(error))]

        declared_name = frontmatter.get("name")
        if not isinstance(declared_name, str) or _NAME.fullmatch(declared_name) is None:
            findings.append(CatalogFinding(relative, "name", "invalid or missing name"))
        elif declared_name != slug:
            findings.append(
                CatalogFinding(
                    relative, "name-directory", f"{declared_name!r} != {slug!r}"
                )
            )

        metadata = frontmatter.get("metadata")
        if not isinstance(metadata, dict):
            findings.append(
                CatalogFinding(relative, "tag-metadata", "metadata must be a mapping")
            )
            return None, findings
        raw_metadata = cast(dict[object, object], metadata)
        raw_tags = raw_metadata.get("aihub.tags")
        if not isinstance(raw_tags, str):
            findings.append(
                CatalogFinding(
                    relative,
                    "tag-metadata",
                    "metadata.aihub.tags must be a JSON-array string",
                )
            )
            return None, findings
        try:
            decoded: object = json.loads(raw_tags)
        except json.JSONDecodeError as error:
            findings.append(
                CatalogFinding(
                    relative,
                    "tag-json",
                    f"metadata.aihub.tags is invalid JSON: {error.msg}",
                )
            )
            return None, findings
        if not isinstance(decoded, list) or not all(
            isinstance(item, str) for item in decoded
        ):
            findings.append(
                CatalogFinding(
                    relative,
                    "tag-type",
                    "metadata.aihub.tags must encode an array of strings",
                )
            )
            return None, findings
        tags = tuple(cast(list[str], decoded))
        if len(tags) != len(set(tags)):
            findings.append(
                CatalogFinding(relative, "tag-duplicate", "tags must be unique")
            )
        if tags != tuple(sorted(tags)):
            findings.append(
                CatalogFinding(relative, "tag-order", "tags must be sorted")
            )
        for tag in tags:
            if _TAG.fullmatch(tag) is None:
                findings.append(
                    CatalogFinding(relative, "tag-syntax", f"invalid tag: {tag}")
                )
                continue
            namespace = tag.split(":", 1)[0]
            if namespace not in _TAG_NAMESPACES:
                findings.append(
                    CatalogFinding(
                        relative, "tag-namespace", f"unsupported tag namespace: {tag}"
                    )
                )
        policy_tags = tuple(tag for tag in tags if tag.startswith("policy:"))
        for tag in policy_tags:
            if tag not in _POLICY_TAGS:
                findings.append(
                    CatalogFinding(relative, "tag-value", f"unsupported tag: {tag}")
                )

        usage, singleton_errors = self._singleton(tags, "usage", _USAGE_TAGS)
        findings.extend(
            CatalogFinding(relative, code, message)
            for code, message in singleton_errors
        )
        updates, singleton_errors = self._singleton(tags, "updates", _UPDATES_TAGS)
        findings.extend(
            CatalogFinding(relative, code, message)
            for code, message in singleton_errors
        )
        provenance_tags = tuple(tag for tag in tags if tag.startswith("provenance:"))
        provenance: str | None = None
        if len(provenance_tags) != 1:
            findings.append(
                CatalogFinding(
                    relative,
                    "tag-required",
                    "expected exactly one provenance:* tag; "
                    f"got {len(provenance_tags)}",
                )
            )
        else:
            provenance = provenance_tags[0].split(":", 1)[1]

        if (usage == "frozen") != (updates == "forbidden"):
            findings.append(
                CatalogFinding(
                    relative,
                    "frozen-contract",
                    "usage:frozen and updates:forbidden must be declared together",
                )
            )

        route: str | None = None
        activation: str | None = None
        detectors = tuple(tag for tag in tags if tag.startswith("detect:"))
        subject_tags = tuple(
            tag for tag in tags if tag.startswith(f"{category.value}:")
        )
        subjects = tuple(tag.split(":", 1)[1] for tag in subject_tags)
        route_tags = tuple(tag for tag in tags if tag.startswith("route:"))
        activation_tags = tuple(tag for tag in tags if tag.startswith("activation:"))
        if category.conditional:
            if len(route_tags) != 1:
                findings.append(
                    CatalogFinding(
                        relative,
                        "route-required",
                        f"expected exactly one route:* tag; got {len(route_tags)}",
                    )
                )
            elif route_tags[0] not in _ROUTE_TAGS:
                findings.append(
                    CatalogFinding(
                        relative, "tag-value", f"unsupported tag: {route_tags[0]}"
                    )
                )
            else:
                route = route_tags[0].split(":", 1)[1]
            if len(activation_tags) != 1:
                findings.append(
                    CatalogFinding(
                        relative,
                        "activation-required",
                        "expected exactly one activation:* tag; "
                        f"got {len(activation_tags)}",
                    )
                )
            elif activation_tags[0] not in _ACTIVATION_TAGS:
                findings.append(
                    CatalogFinding(
                        relative,
                        "tag-value",
                        f"unsupported tag: {activation_tags[0]}",
                    )
                )
            else:
                activation = activation_tags[0].split(":", 1)[1]
            if not subjects:
                findings.append(
                    CatalogFinding(
                        relative,
                        "category-tag-required",
                        f"{category.value} skills require {category.value}:*",
                    )
                )
            requires_detection = activation in {"detected", "detected-or-opt-in"}
            has_runtime_detector = any(
                not tag.startswith("detect:opt-in:") for tag in detectors
            )
            if requires_detection and not has_runtime_detector:
                findings.append(
                    CatalogFinding(
                        relative,
                        "detector-required",
                        f"activation:{activation} requires a non-opt-in detect:* tag",
                    )
                )
            if activation in {"opt-in", "detected-or-opt-in"} and not any(
                tag.startswith("detect:opt-in:") for tag in detectors
            ):
                findings.append(
                    CatalogFinding(
                        relative,
                        "detector-required",
                        f"activation:{activation} requires detect:opt-in:*",
                    )
                )
            for detector in detectors:
                message = self._detector_error(detector)
                if message is not None:
                    findings.append(CatalogFinding(relative, "detector", message))
        elif route_tags or activation_tags or detectors:
            findings.append(
                CatalogFinding(
                    relative,
                    "distribution-tag",
                    f"{category.value} distribution is owned only by its path",
                )
            )

        if findings or usage is None or updates is None or provenance is None:
            return None, findings
        return (
            SkillRecord(
                name=slug,
                category=category,
                directory=skill_file.parent,
                tags=tags,
                usage=usage,
                updates=updates,
                provenance=provenance,
                route=route,
                activation=activation,
                subjects=subjects,
                detectors=detectors,
            ),
            [],
        )

    def _discover(
        self,
    ) -> tuple[tuple[Path, ...], tuple[SkillRecord, ...], tuple[CatalogFinding, ...]]:
        skills_root = self.root / "skills"
        if not skills_root.is_dir():
            return (), (), ()
        directories: list[Path] = []
        records: list[SkillRecord] = []
        findings: list[CatalogFinding] = []
        names: dict[str, Path] = {}
        for skill_file in sorted(skills_root.rglob("SKILL.md")):
            relative = skill_file.relative_to(skills_root)
            if len(relative.parts) != 3 or relative.name != "SKILL.md":
                findings.append(
                    CatalogFinding(
                        self._relative(self.root, skill_file),
                        "skill-path",
                        "skill must be skills/<category>/<slug>/SKILL.md",
                    )
                )
                continue
            raw_category, slug, _filename = relative.parts
            try:
                category = SkillCategory(raw_category)
            except ValueError:
                findings.append(
                    CatalogFinding(
                        self._relative(self.root, skill_file),
                        "skill-category",
                        f"unsupported skill category: {raw_category}",
                    )
                )
                continue
            directories.append(skill_file.parent)
            record, record_findings = self._parse_record(skill_file, category, slug)
            findings.extend(record_findings)
            if record is None:
                continue
            first_path = names.get(record.name)
            if first_path is not None:
                findings.append(
                    CatalogFinding(
                        self._relative(self.root, skill_file),
                        "duplicate",
                        f"duplicate skill name: {record.name}",
                    )
                )
                continue
            names[record.name] = skill_file
            records.append(record)
        return (
            tuple(sorted(directories)),
            tuple(
                sorted(records, key=lambda record: (record.name, record.category.value))
            ),
            tuple(
                sorted(
                    findings,
                    key=lambda finding: (
                        finding.path,
                        finding.code,
                        finding.message,
                    ),
                )
            ),
        )

    def contract_findings(self) -> tuple[CatalogFinding, ...]:
        """Return all path and semantic metadata defects without mutation."""

        return self._findings

    def require_valid(self) -> None:
        """Fail before a consumer publishes or mutates an invalid catalog."""

        if self._findings:
            first = self._findings[0]
            raise ValueError(f"{first.path}: {first.code}: {first.message}")

    def records(self) -> tuple[SkillRecord, ...]:
        """Return the complete typed catalog after enforcing its contract."""

        self.require_valid()
        return self._records

    def skill_dirs(self) -> tuple[Path, ...]:
        """Return recursively discovered canonical bundle directories."""

        return self._directories

    def record(self, name: str) -> SkillRecord:
        """Resolve exactly one validated skill by canonical name."""

        self.require_valid()
        selected = tuple(record for record in self._records if record.name == name)
        if len(selected) != 1:
            raise KeyError(f"unknown canonical skill: {name}")
        return selected[0]

    def _distributions(self, record: SkillRecord) -> tuple[str, ...]:
        if record.updates == "forbidden":
            return ()
        if record.category == SkillCategory.AGENT_WIDE:
            return ("personal",)
        if record.category == SkillCategory.PROJECT_WIDE:
            return ("project-generic",)
        route = "project" if record.route == "project" else "agent"
        return tuple(
            f"{route}-capability:{record.category.value}:{subject}"
            for subject in record.subjects
        )

    def _policy(self, record: SkillRecord) -> SkillPolicy:
        budgets = cast(dict[str, int], self.config["budgets"])
        if record.updates == "forbidden" or record.usage == "frozen":
            max_tokens = budgets["frozen_tokens"]
        elif record.usage == "router":
            max_tokens = budgets["router_tokens"]
        else:
            max_tokens = budgets["on_demand_tokens"]
        return SkillPolicy(
            name=record.name,
            class_name=record.usage.replace("-", "_"),
            provenance=record.provenance,
            updates=record.updates,
            max_tokens=max_tokens,
            max_lines=budgets["max_lines"],
            distributions=self._distributions(record),
            category=record.category,
            tags=record.tags,
        )

    def policy(self, name: str) -> SkillPolicy:
        return self._policy(self.record(name))

    def policy_for(self, directory: Path) -> SkillPolicy:
        """Resolve policy by physical source path without basename ambiguity."""

        self.require_valid()
        canonical = directory.resolve()
        selected = tuple(
            record
            for record in self._records
            if record.directory.resolve() == canonical
        )
        if len(selected) != 1:
            raise KeyError(f"unknown canonical skill directory: {directory}")
        return self._policy(selected[0])

    def names_for(self, distribution: str) -> frozenset[str]:
        """Return the path/tag-derived, fail-closed selection for one surface."""

        return frozenset(
            record.name
            for record in self.records()
            if distribution in self._distributions(record)
        )

    @staticmethod
    def _detector_profile(records: list[SkillRecord]) -> dict[str, Any]:
        markers: set[str] = set()
        dependencies: dict[str, set[str]] = defaultdict(set)
        owned_extensions: set[str] = set()
        owned_globs: set[str] = set()
        opt_ins: set[str] = set()
        selected_tags: set[str] = set()
        for record in records:
            for tag in record.detectors:
                parts = tag.split(":", 3)
                kind = parts[1]
                if kind == "marker":
                    markers.add(":".join(parts[2:]))
                elif kind == "dependency":
                    dependencies[parts[2]].add(parts[3])
                elif kind == "owned-extension":
                    owned_extensions.add(":".join(parts[2:]))
                elif kind == "owned-glob":
                    owned_globs.add(":".join(parts[2:]))
                elif kind == "opt-in":
                    opt_ins.add(":".join(parts[2:]))
                elif kind == "selected-tag":
                    selected_tags.add(":".join(parts[2:]))
        return {
            "markers": sorted(markers),
            "dependencies": {
                ecosystem: sorted(names)
                for ecosystem, names in sorted(dependencies.items())
            },
            "owned_extensions": sorted(owned_extensions),
            "owned_globs": sorted(owned_globs),
            "opt_ins": sorted(opt_ins),
            "selected_tags": sorted(selected_tags),
            "skills": sorted(record.name for record in records),
        }

    def conditional_project_profiles(self) -> dict[str, dict[str, Any]]:
        """Derive category-qualified project capabilities from semantic tags."""

        grouped: dict[str, list[SkillRecord]] = defaultdict(list)
        for record in self.records():
            if not record.category.conditional or record.route != "project":
                continue
            for subject in record.subjects:
                grouped[f"{record.category.value}:{subject}"].append(record)
        return {
            capability: self._detector_profile(records)
            for capability, records in sorted(grouped.items())
        }

    def distribution_errors(self) -> tuple[str, ...]:
        """Compatibility view over the typed semantic contract findings."""

        return tuple(f"{finding.path}: {finding.message}" for finding in self._findings)

    @staticmethod
    def physical_tree_contract(directory: Path) -> str:
        """Hash bytes, entry kinds, and permissions for one physical bundle."""

        digest = hashlib.sha256()
        root_metadata = directory.lstat()
        paths: tuple[Path, ...]
        if stat.S_ISLNK(root_metadata.st_mode):
            raise ValueError(f"symlink forbidden in physical bundle: {directory}")
        if stat.S_ISREG(root_metadata.st_mode):
            paths = (directory,)
            root_is_file = True
        elif stat.S_ISDIR(root_metadata.st_mode):
            paths = (directory, *sorted(directory.rglob("*")))
            root_is_file = False
        else:
            raise ValueError(f"unsupported file type in physical bundle: {directory}")
        for path in paths:
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"symlink forbidden in physical bundle: {path}")
            if stat.S_ISREG(metadata.st_mode):
                entry_type = "file"
            elif stat.S_ISDIR(metadata.st_mode):
                entry_type = "directory"
            else:
                raise ValueError(f"unsupported file type in physical bundle: {path}")
            relative = (
                "."
                if root_is_file
                else (
                    "." if path == directory else path.relative_to(directory).as_posix()
                )
            )
            digest.update(entry_type.encode())
            digest.update(b"\0")
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(f"{stat.S_IMODE(metadata.st_mode):04o}".encode())
            digest.update(b"\0")
            if entry_type == "file":
                digest.update(path.read_bytes())
                digest.update(b"\0")
        return digest.hexdigest()

    @staticmethod
    def digest_tree(directory: Path) -> str:
        """Return the deterministic content identity after physical validation."""

        Catalog.physical_tree_contract(directory)
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
        for record in self.records():
            policy = self._policy(record)
            entries.append(
                {
                    "name": record.name,
                    "owner": "agents",
                    "category": record.category.value,
                    "class": policy.class_name,
                    "provenance": policy.provenance,
                    "updates": policy.updates,
                    "max_tokens": policy.max_tokens,
                    "max_lines": policy.max_lines,
                    "distributions": list(policy.distributions),
                    "tags": list(record.tags),
                    "path": record.directory.relative_to(self.root).as_posix(),
                    "digest": self.digest_tree(record.directory),
                }
            )
        return entries

    def inventory_payload(self) -> dict[str, Any]:
        """Return the single versioned document written to the inventory lock."""

        return {"version": _INVENTORY_VERSION, "skills": self.inventory()}

    def render_inventory(self) -> str:
        """Render the canonical inventory lock deterministically."""

        return json.dumps(self.inventory_payload(), indent=2, sort_keys=True) + "\n"

    def inventory_lock_findings(
        self, *, required: bool = True
    ) -> tuple[CatalogFinding, ...]:
        """Compare the checked-in inventory lock without mutating it."""

        path = self.root / "skills.lock.json"
        relative = path.relative_to(self.root).as_posix()
        if not path.is_file():
            if not required:
                return ()
            return (
                CatalogFinding(
                    relative,
                    "inventory-lock-missing",
                    "canonical skill inventory lock is missing",
                ),
            )
        try:
            current = path.read_text(encoding="utf-8")
            loaded = json.loads(current)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            return (
                CatalogFinding(
                    relative,
                    "inventory-lock-invalid",
                    f"canonical skill inventory lock is unreadable: {error}",
                ),
            )
        expected = self.render_inventory()
        if loaded != self.inventory_payload() or current != expected:
            return (
                CatalogFinding(
                    relative,
                    "inventory-lock-drift",
                    "canonical skill inventory lock differs from discovery",
                ),
            )
        return ()
