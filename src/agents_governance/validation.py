"""Blocking validation for the canonical skill authority."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .agent_profiles import audit_agent_profiles
from .catalog import (
    NON_PORTABLE_PROJECT_REFERENCE,
    Catalog,
    SkillCategory,
    SkillRecord,
)
from .commands import audit_command_specs
from .rules import audit_rule_specs
from .skill_metadata import validate as validate_skill_metadata
from .tokens import bpe_tokens
from .waza import EvalRole, EvalSpecError, EvalTaskSpec, load_eval_suite
from .waza import findings as waza_config_findings

_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_FENCED_CODE = re.compile(r"^```.*?^```\s*$", re.MULTILINE | re.DOTALL)
_DESCRIPTION_MIN_CHARACTERS = 12
_DESCRIPTION_MAX_CHARACTERS = 96
_DESCRIPTION_MIN_TERMS = 3
_DESCRIPTION_MAX_TERMS = 10
_DESCRIPTION_TOKEN = r"[a-z0-9](?:[a-z0-9+./_-]*[a-z0-9+])?"
_DESCRIPTION_TERM = re.compile(rf"{_DESCRIPTION_TOKEN}(?: {_DESCRIPTION_TOKEN}){{0,2}}")
_DESCRIPTION_PROSE_MARKERS = frozenset(
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
_GENERIC_HELLO = re.compile(
    r'def\s+hello\s*\(\s*name\s*\)\s*:.*return\s+f?["\']Hello,\s*\{name\}!['
    r'"\']',
    re.DOTALL,
)
_GENERIC_PROMPT_MARKERS = (
    "help me with this task",
    "capability to the provided fixture. exercise these requirements:",
    "request safely. relevant capability:",
    "what is the weather today?",
)
_GENERIC_ASSERTIONS = {
    "completed",
    "function",
    "result",
    "skill activated",
    "success",
    "validation",
}


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


def description_contract_error(value: object) -> str | None:
    """Return why a skill discovery description is not a compact keyword list."""

    if not isinstance(value, str) or not value:
        return "missing description"
    if value != value.strip() or "\n" in value or "\r" in value:
        return "description must be one trimmed line"
    if not (_DESCRIPTION_MIN_CHARACTERS <= len(value) <= _DESCRIPTION_MAX_CHARACTERS):
        return "description must contain 12-96 characters"
    if value != value.casefold():
        return "description must use lowercase terms"
    if re.search(r",(?! )| ,", value):
        return "description terms must be separated by ', '"
    terms = value.split(", ")
    if not (_DESCRIPTION_MIN_TERMS <= len(terms) <= _DESCRIPTION_MAX_TERMS):
        return "description must contain 3-10 unique terms"
    if len(set(terms)) != len(terms):
        return "description terms must be unique"
    if any(
        marker in term.split()
        for term in terms
        for marker in _DESCRIPTION_PROSE_MARKERS
    ):
        return "description must contain keywords or nominal phrases, not prose"
    if any(_DESCRIPTION_TERM.fullmatch(term) is None for term in terms):
        return (
            "description terms may contain only lowercase words and technical "
            "identifiers"
        )
    return None


def _eval_findings(root: Path, records: tuple[SkillRecord, ...]) -> list[Finding]:
    """Reject Waza suites that cannot prove three semantic behaviors."""

    eval_root = root / "evals"
    if not eval_root.exists():
        return []
    findings: list[Finding] = []
    seen_task_ids: set[str] = set()
    seen_prompts: dict[str, Path] = {}
    for record in sorted(records, key=lambda item: item.name):
        name = record.name
        directory = eval_root / name
        config_path = directory / "eval.yaml"
        relative = config_path.relative_to(root).as_posix()
        if not config_path.is_file():
            findings.append(Finding(relative, "eval-missing", "missing eval.yaml"))
            continue
        try:
            suite = load_eval_suite(directory)
        except EvalSpecError as error:
            error_path = error.path.relative_to(root).as_posix()
            findings.append(Finding(error_path, "eval-schema", str(error)))
            continue
        if (
            suite.skill != name
            or suite.required_skills != (name,)
            or suite.skill_directories
            != (f"../../skills/{record.category.value}/{name}",)
        ):
            findings.append(
                Finding(
                    relative, "eval-skill", "eval must bind exactly its canonical skill"
                )
            )
        raw_config = config_path.read_text(encoding="utf-8")
        if "relevant_content" in raw_config:
            findings.append(
                Finding(
                    relative,
                    "eval-generic",
                    "generic relevant_content grader is forbidden",
                )
            )
        prompt_graders = [grader for grader in suite.graders if grader.kind == "prompt"]
        if not any(
            grader.prompt
            and name.casefold() in grader.prompt.casefold()
            and grader.name
            and name.casefold() in grader.name.casefold()
            for grader in prompt_graders
        ):
            findings.append(
                Finding(
                    relative,
                    "eval-grader",
                    "prompt grader must be named and written for the canonical skill",
                )
            )
        behavior_graders = [
            grader for grader in suite.graders if grader.kind == "behavior"
        ]
        timeout_ms = (
            suite.timeout_seconds * 1000
            if suite.timeout_seconds is not None and suite.timeout_seconds > 0
            else None
        )
        if (
            timeout_ms is None
            or len(behavior_graders) != 1
            or behavior_graders[0].max_duration_ms is None
            or behavior_graders[0].max_duration_ms <= 0
            or behavior_graders[0].max_duration_ms >= timeout_ms
        ):
            findings.append(
                Finding(
                    relative,
                    "eval-duration",
                    "one positive behavior duration must be shorter than executor timeout",
                )
            )
        roles = [task.role for task in suite.tasks]
        if len(suite.tasks) != len(EvalRole) or set(roles) != set(EvalRole):
            rendered = ", ".join(
                role.value if role is not None else "unknown" for role in roles
            )
            findings.append(
                Finding(
                    relative,
                    "eval-roles",
                    "task roles must be exactly happy_path, fail_closed, "
                    f"should_not_trigger; got [{rendered}]",
                )
            )
        for task in suite.tasks:
            task_relative = task.path.relative_to(root).as_posix()
            if not task.identifier or task.identifier in seen_task_ids:
                findings.append(
                    Finding(
                        task_relative,
                        "eval-id",
                        "task id must be non-empty and unique across the eval corpus",
                    )
                )
            else:
                seen_task_ids.add(task.identifier)
            prompt = task.prompt.strip() if task.prompt else ""
            if not prompt and task.role != EvalRole.FAIL_CLOSED:
                findings.append(
                    Finding(task_relative, "eval-prompt", "empty task prompt")
                )
            folded_prompt = prompt.casefold()
            if folded_prompt:
                first_prompt = seen_prompts.get(folded_prompt)
                if first_prompt is not None:
                    findings.append(
                        Finding(
                            task_relative,
                            "eval-prompt-duplicate",
                            "task prompt duplicates "
                            f"{first_prompt.relative_to(root).as_posix()}",
                        )
                    )
                else:
                    seen_prompts[folded_prompt] = task.path
            if any(marker in folded_prompt for marker in _GENERIC_PROMPT_MARKERS):
                findings.append(
                    Finding(
                        task_relative,
                        "eval-scaffold",
                        "generated capability scaffold is forbidden",
                    )
                )
            skill_text = (record.directory / "SKILL.md").read_text(encoding="utf-8")
            try:
                metadata, _body = _frontmatter(skill_text)
            except (TypeError, ValueError, yaml.YAMLError):
                metadata = {}
            description = metadata.get("description")
            if (
                isinstance(description, str)
                and description.strip()
                and description.casefold() in folded_prompt
            ):
                findings.append(
                    Finding(
                        task_relative,
                        "eval-description-copy",
                        "prompt copies the discovery description instead of a user task",
                    )
                )
            findings.extend(_task_assertion_findings(root, task))
            findings.extend(_fixture_reference_findings(root, directory, task))
        findings.extend(_fixture_tree_findings(root, directory))
    return findings


def _material_assertions(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        value
        for value in values
        if value.strip().casefold() not in _GENERIC_ASSERTIONS
        and len(value.strip()) >= 4
    )


def _task_assertion_findings(root: Path, task: EvalTaskSpec) -> list[Finding]:
    relative = task.path.relative_to(root).as_posix()
    positive = _material_assertions(task.output_contains)
    negative = _material_assertions(task.output_not_contains)
    findings: list[Finding] = []
    if task.outcomes == ("task_completed",) and not positive and not negative:
        findings.append(
            Finding(
                relative,
                "eval-assertion",
                "task_completed alone does not prove a material result",
            )
        )
    if task.role == EvalRole.HAPPY_PATH and not positive:
        findings.append(
            Finding(
                relative,
                "eval-assertion",
                "happy_path requires a specific positive result or artifact assertion",
            )
        )
    elif task.role == EvalRole.FAIL_CLOSED and (not positive or not negative):
        findings.append(
            Finding(
                relative,
                "eval-assertion",
                "fail_closed requires a blocking result and a forbidden-action assertion",
            )
        )
    elif task.role == EvalRole.SHOULD_NOT_TRIGGER and not negative:
        findings.append(
            Finding(
                relative,
                "eval-antitrigger",
                "should_not_trigger requires a skill-specific negative assertion",
            )
        )
    return findings


def _fixture_reference_findings(
    root: Path, directory: Path, task: EvalTaskSpec
) -> list[Finding]:
    findings: list[Finding] = []
    relative = task.path.relative_to(root).as_posix()
    fixture_root = directory / "fixtures"
    for raw_path in task.fixture_paths:
        fixture_path = Path(raw_path)
        if fixture_path.is_absolute() or ".." in fixture_path.parts:
            findings.append(
                Finding(
                    relative,
                    "eval-fixture",
                    f"fixture path must remain inside the suite: {raw_path}",
                )
            )
            continue
        candidate = fixture_root / fixture_path
        current = fixture_root
        contains_symlink = fixture_root.is_symlink()
        for part in fixture_path.parts:
            current /= part
            contains_symlink = contains_symlink or current.is_symlink()
        if contains_symlink:
            findings.append(
                Finding(
                    relative,
                    "eval-fixture-symlink",
                    f"fixture path traverses a symlink: {raw_path}",
                )
            )
            continue
        if not candidate.is_file():
            findings.append(
                Finding(
                    relative,
                    "eval-fixture",
                    f"fixture is missing or not a regular file: {raw_path}",
                )
            )
            continue
        try:
            candidate.resolve(strict=True).relative_to(
                fixture_root.resolve(strict=True)
            )
        except (FileNotFoundError, ValueError):
            findings.append(
                Finding(
                    relative,
                    "eval-fixture",
                    f"fixture resolves outside the suite: {raw_path}",
                )
            )
    return findings


def _fixture_tree_findings(root: Path, directory: Path) -> list[Finding]:
    fixture_root = directory / "fixtures"
    if fixture_root.is_symlink():
        return [
            Finding(
                fixture_root.relative_to(root).as_posix(),
                "eval-fixture-symlink",
                "the eval fixture root cannot be a symlink",
            )
        ]
    if not fixture_root.exists():
        return []
    findings: list[Finding] = []
    for fixture in sorted(fixture_root.rglob("*")):
        relative = fixture.relative_to(root).as_posix()
        if fixture.is_symlink():
            findings.append(
                Finding(
                    relative,
                    "eval-fixture-symlink",
                    "symlinks are forbidden in eval fixtures",
                )
            )
            continue
        if fixture.is_file() and _GENERIC_HELLO.search(
            fixture.read_text(encoding="utf-8", errors="replace")
        ):
            findings.append(
                Finding(
                    relative,
                    "eval-fixture-generic",
                    "generic hello(name) fixture cannot prove skill behavior",
                )
            )
    return findings


def validate(catalog: Catalog) -> list[Finding]:
    """Validate canonical profiles and every active skill."""

    agent_audit = audit_agent_profiles(catalog.root)
    findings = [
        Finding(item.path, item.code, item.message) for item in agent_audit.findings
    ]
    findings.extend(
        Finding(item.path, item.code, item.message)
        for item in validate_skill_metadata(catalog.root)
    )
    command_audit = audit_command_specs(
        catalog.root, (directory.name for directory in catalog.skill_dirs())
    )
    findings.extend(
        Finding(item.path, item.code, item.message) for item in command_audit.findings
    )
    rule_audit = audit_rule_specs(catalog.root)
    findings.extend(
        Finding(item.path, item.code, item.message) for item in rule_audit.findings
    )
    records = catalog.records()
    if (catalog.root / ".waza.yaml").is_file():
        for waza_item in waza_config_findings(catalog.root):
            findings.append(
                Finding(
                    waza_item.path.relative_to(catalog.root).as_posix(),
                    "eval-model-drift",
                    f"model {waza_item.actual!r} != project default {waza_item.expected!r}",
                )
            )
    skills_root = catalog.root / "skills"
    for category in SkillCategory:
        category_root = skills_root / category.value
        if not category_root.is_dir():
            continue
        for directory in sorted(category_root.iterdir()):
            if (
                directory.name.startswith(".")
                or not directory.is_dir()
                or (directory / "SKILL.md").is_file()
            ):
                continue
            findings.append(
                Finding(
                    directory.relative_to(catalog.root).as_posix(),
                    "orphan-skill-directory",
                    "skill namespace directory has no SKILL.md",
                )
            )
    project_directories = {
        record.directory
        for record in records
        if record.category == SkillCategory.PROJECT_WIDE
        or (record.category.conditional and record.route == "project")
    }
    for record in records:
        directory = record.directory
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
        description = metadata.get("description")
        description_error = description_contract_error(description)
        if description_error is not None:
            findings.append(Finding(relative, "description", description_error))
        policy = catalog.policy(record.name)
        if directory in project_directories:
            for project_file in sorted(
                path
                for path in directory.rglob("*")
                if path.is_file() and not path.is_symlink()
            ):
                project_text = project_file.read_text(
                    encoding="utf-8", errors="replace"
                )
                if NON_PORTABLE_PROJECT_REFERENCE.search(project_text):
                    findings.append(
                        Finding(
                            project_file.relative_to(catalog.root).as_posix(),
                            "non-generic",
                            "project-distributed skill contains private or cross-repository contract",
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
    findings.extend(_eval_findings(catalog.root, records))
    return findings
