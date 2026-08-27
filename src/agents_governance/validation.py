"""Blocking validation for the canonical skill authority."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .catalog import Catalog
from .model_pipeline import findings as model_pipeline_findings
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


def _eval_findings(root: Path, skill_names: set[str]) -> list[Finding]:
    """Reject missing, generic, or structurally empty Waza specifications."""

    eval_root = root / "evals"
    if not eval_root.exists():
        return []
    findings: list[Finding] = []
    for name in sorted(skill_names):
        directory = eval_root / name
        config_path = directory / "eval.yaml"
        relative = config_path.relative_to(root).as_posix()
        if not config_path.is_file():
            findings.append(Finding(relative, "eval-missing", "missing eval.yaml"))
            continue
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            findings.append(Finding(relative, "eval-yaml", str(error)))
            continue
        if not isinstance(config, dict):
            findings.append(Finding(relative, "eval-schema", "eval must be a mapping"))
            continue
        settings = config.get("config")
        required = (
            settings.get("required_skills") if isinstance(settings, dict) else None
        )
        directories = (
            settings.get("skill_directories") if isinstance(settings, dict) else None
        )
        if required != [name] or directories != [f"../../skills/{name}"]:
            findings.append(
                Finding(
                    relative, "eval-skill", "eval must bind exactly its canonical skill"
                )
            )
        graders = config.get("graders")
        if "relevant_content" in str(graders):
            findings.append(
                Finding(
                    relative,
                    "eval-generic",
                    "generic relevant_content grader is forbidden",
                )
            )
        task_paths = sorted((directory / "tasks").glob("*.yaml"))
        if not task_paths:
            findings.append(Finding(relative, "eval-tasks", "no task specifications"))
        for task_path in task_paths:
            task_relative = task_path.relative_to(root).as_posix()
            try:
                task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as error:
                findings.append(Finding(task_relative, "eval-yaml", str(error)))
                continue
            inputs = task.get("inputs") if isinstance(task, dict) else None
            prompt = inputs.get("prompt") if isinstance(inputs, dict) else None
            if not isinstance(prompt, str) or not prompt.strip():
                findings.append(
                    Finding(task_relative, "eval-prompt", "empty task prompt")
                )
            elif prompt.strip() == "Help me with this task":
                findings.append(
                    Finding(task_relative, "eval-generic", "generic task prompt")
                )
            expected = task.get("expected") if isinstance(task, dict) else None
            output_contains = (
                expected.get("output_contains") if isinstance(expected, dict) else None
            )
            if isinstance(output_contains, list) and any(
                value == "function" for value in output_contains
            ):
                findings.append(
                    Finding(task_relative, "eval-generic", "generic function assertion")
                )
    return findings


def validate(catalog: Catalog) -> list[Finding]:
    """Validate every active skill and return all blocking findings."""

    findings: list[Finding] = []
    if (catalog.root / "config" / "skills.json").is_file():
        findings.extend(
            Finding("config/skills.json", "distribution", message)
            for message in catalog.distribution_errors()
        )
    if (catalog.root / "config" / "model-pipeline.json").is_file():
        for pipeline_item in model_pipeline_findings(catalog.root):
            findings.append(
                Finding(
                    pipeline_item.path.relative_to(catalog.root).as_posix(),
                    "model-pipeline-drift",
                    pipeline_item.message,
                )
            )
    names: set[str] = set()
    for directory in sorted((catalog.root / "skills").iterdir()):
        if directory.is_dir() and not (directory / "SKILL.md").is_file():
            findings.append(
                Finding(
                    directory.relative_to(catalog.root).as_posix(),
                    "orphan-skill-directory",
                    "skill namespace directory has no SKILL.md",
                )
            )
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
    findings.extend(_eval_findings(catalog.root, names))
    return findings
