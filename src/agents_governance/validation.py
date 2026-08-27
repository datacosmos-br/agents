"""Blocking validation for the canonical skill authority."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass

import yaml

from .catalog import Catalog
from .tokens import bpe_tokens

_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_FENCED_CODE = re.compile(r"^```.*?^```\s*$", re.MULTILINE | re.DOTALL)
_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DESCRIPTION_KEYWORD = re.compile(r"^[a-z0-9][a-z0-9+./:_-]*$")
_PRIVATE_PROJECT_TERM = re.compile(
    r"(?:~/(?:\.agents|gt)(?:/|\b)|/home/[^/\s]+/|\.beads(?:/|\b)|\b(?:Gas Town|AI Hub|Beads)\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    """One deterministic validation failure."""

    path: str
    code: str
    message: str


def _frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise ValueError("unterminated YAML frontmatter")
    loaded = yaml.safe_load(text[4:marker])
    if not isinstance(loaded, dict):
        raise TypeError("frontmatter must be a mapping")
    return loaded, text[marker + 5 :]


def validate(catalog: Catalog) -> list[Finding]:
    """Validate every active skill and return all blocking findings."""

    findings: list[Finding] = []
    names: set[str] = set()
    technology_names = {
        skill
        for profile in catalog.technology_profiles().values()
        for skill in profile["skills"]
    }
    generic_names = set(catalog.config.get("project_generic", []))
    overlap = technology_names & generic_names
    for name in sorted(overlap):
        findings.append(Finding("config/skills.json", "distribution-overlap", name))
    for pattern in catalog.config.get("private_patterns", []):
        for name in sorted(generic_names):
            if fnmatch.fnmatchcase(name, pattern):
                findings.append(
                    Finding("config/skills.json", "private-project-skill", name)
                )
    for directory in catalog.skill_dirs():
        skill_file = directory / "SKILL.md"
        relative = skill_file.relative_to(catalog.root).as_posix()
        text = skill_file.read_text(encoding="utf-8")
        for item in directory.rglob("*"):
            if item.is_symlink():
                findings.append(
                    Finding(
                        item.relative_to(catalog.root).as_posix(),
                        "symlink",
                        "forbidden in skill bundle",
                    )
                )
        try:
            metadata, _body = _frontmatter(text)
        except (TypeError, ValueError, yaml.YAMLError) as error:
            findings.append(Finding(relative, "frontmatter", str(error)))
            continue
        name = metadata.get("name")
        description = metadata.get("description")
        if not isinstance(name, str) or not _NAME.fullmatch(name):
            findings.append(Finding(relative, "name", "invalid or missing name"))
        elif name != directory.name:
            findings.append(
                Finding(relative, "name-directory", f"{name!r} != {directory.name!r}")
            )
        elif name in names:
            findings.append(Finding(relative, "duplicate", f"duplicate name: {name}"))
        else:
            names.add(name)
        if not isinstance(description, str) or not description.strip():
            findings.append(Finding(relative, "description", "missing description"))
        elif len(description) > 120:
            findings.append(
                Finding(
                    relative,
                    "description",
                    "keyword description exceeds 120 characters",
                )
            )
        else:
            keywords = [item.strip() for item in description.split(",")]
            if len(keywords) < 2 or any(
                not _DESCRIPTION_KEYWORD.fullmatch(item) for item in keywords
            ):
                findings.append(
                    Finding(
                        relative,
                        "description",
                        "description must be a comma-separated keyword list",
                    )
                )
            elif len(keywords) > 10:
                findings.append(
                    Finding(relative, "description", "description exceeds 10 keywords")
                )
        policy = catalog.policy(directory.name)
        if directory.name in generic_names:
            for project_file in sorted(
                path for path in directory.rglob("*") if path.is_file()
            ):
                project_text = project_file.read_text(
                    encoding="utf-8", errors="replace"
                )
                if _PRIVATE_PROJECT_TERM.search(project_text):
                    findings.append(
                        Finding(
                            project_file.relative_to(catalog.root).as_posix(),
                            "non-generic",
                            "project-generic skill contains private or cross-repository contract",
                        )
                    )
        token_estimate = bpe_tokens(skill_file, catalog.root)
        if token_estimate > policy.max_tokens:
            findings.append(
                Finding(
                    relative, "budget", f"{token_estimate} > {policy.max_tokens} tokens"
                )
            )
        if len(text.splitlines()) > policy.max_lines:
            findings.append(
                Finding(
                    relative,
                    "lines",
                    f"{len(text.splitlines())} > {policy.max_lines} lines",
                )
            )
        markdown_files = [skill_file, *sorted(directory.rglob("*.md"))]
        for markdown_file in dict.fromkeys(markdown_files):
            markdown_text = markdown_file.read_text(encoding="utf-8")
            markdown_text = _FENCED_CODE.sub("", markdown_text)
            markdown_relative = markdown_file.relative_to(catalog.root).as_posix()
            for target in _LINK.findall(markdown_text):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                clean_target = target.split("#", 1)[0]
                if not clean_target:
                    continue
                if "/" not in clean_target and "." not in clean_target:
                    continue
                candidate = markdown_file.parent / clean_target
                try:
                    resolved = candidate.resolve(strict=True)
                    resolved.relative_to(directory.resolve())
                except (FileNotFoundError, ValueError):
                    findings.append(
                        Finding(
                            markdown_relative,
                            "reference",
                            f"unsafe or missing: {target}",
                        )
                    )
    return findings
