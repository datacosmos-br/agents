"""First-defect validation of the complete canonical authority."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from .agent_profiles import AgentProfile
from .catalog import NON_PORTABLE_PROJECT_REFERENCE, Catalog, SkillCategory, SkillRecord
from .commands import CommandSpec
from .rules import RuleSpec
from .skill_metadata import validate as validate_skill_metadata
from .tokens import bpe_tokens
from .waza import EvalRole, EvalTaskSpec, load_eval_suite

_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_FENCED_CODE = re.compile(r"^```.*?^```\s*$", re.MULTILINE | re.DOTALL)
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
_GENERIC_HELLO = re.compile(
    r'def\s+hello\s*\(\s*name\s*\)\s*:.*return\s+f?["\']Hello,\s*\{name\}!["\']',
    re.DOTALL,
)
_GENERIC_PROMPTS = (
    "help me with this task",
    "capability to the provided fixture. exercise these requirements:",
    "request safely. relevant capability:",
    "what is the weather today?",
)
_GENERIC_ASSERTIONS = frozenset(
    {"completed", "function", "result", "skill activated", "success", "validation"}
)


def require_description(value: object) -> str:
    """Return a valid discovery description or raise on its first defect."""

    if not isinstance(value, str) or not value:
        raise ValueError("missing description")
    if value != value.strip() or "\n" in value or "\r" in value:
        raise ValueError("description must be one trimmed line")
    if not 12 <= len(value) <= 96:
        raise ValueError("description must contain 12-96 characters")
    if value != value.casefold():
        raise ValueError("description must use lowercase terms")
    if re.search(r",(?! )| ,", value):
        raise ValueError("description terms must be separated by ', '")
    terms = value.split(", ")
    if not 3 <= len(terms) <= 10:
        raise ValueError("description must contain 3-10 unique terms")
    if len(terms) != len(set(terms)):
        raise ValueError("description terms must be unique")
    if any(marker in term.split() for term in terms for marker in _PROSE_MARKERS):
        raise ValueError(
            "description must contain keywords or nominal phrases, not prose"
        )
    if any(_DESCRIPTION_TERM.fullmatch(term) is None for term in terms):
        raise ValueError(
            "description terms may contain only lowercase words and technical identifiers"
        )
    return value


def _material(values: tuple[str, ...]) -> bool:
    return any(
        len(value.strip()) >= 4 and value.strip().casefold() not in _GENERIC_ASSERTIONS
        for value in values
    )


def _require_task(
    root: Path,
    suite_root: Path,
    task: EvalTaskSpec,
    seen_ids: set[str],
    seen_prompts: set[str],
    description: str,
) -> None:
    if not task.identifier:
        raise ValueError(f"{task.path}: task id is required")
    if task.identifier in seen_ids:
        raise ValueError(f"{task.path}: task id is duplicated: {task.identifier}")
    seen_ids.add(task.identifier)
    prompt = task.prompt.strip() if task.prompt is not None else ""
    if not prompt and task.role is not EvalRole.FAIL_CLOSED:
        raise ValueError(f"{task.path}: task prompt is required")
    folded = prompt.casefold()
    if folded:
        if folded in seen_prompts:
            raise ValueError(f"{task.path}: task prompt is duplicated")
        seen_prompts.add(folded)
    if any(marker in folded for marker in _GENERIC_PROMPTS):
        raise ValueError(f"{task.path}: generated capability scaffold is forbidden")
    if description.casefold() in folded:
        raise ValueError(f"{task.path}: task copies the discovery description")
    positive = _material(task.output_contains)
    negative = _material(task.output_not_contains)
    if task.outcomes == ("task_completed",) and not positive and not negative:
        raise ValueError(
            f"{task.path}: task_completed does not prove a material result"
        )
    if task.role is EvalRole.HAPPY_PATH and not positive:
        raise ValueError(
            f"{task.path}: happy_path requires a material positive assertion"
        )
    if task.role is EvalRole.FAIL_CLOSED and (not positive or not negative):
        raise ValueError(
            f"{task.path}: fail_closed requires blocking and forbidden-action assertions"
        )
    if task.role is EvalRole.SHOULD_NOT_TRIGGER and not negative:
        raise ValueError(
            f"{task.path}: should_not_trigger requires a material negative assertion"
        )
    fixture_root = suite_root / "fixtures"
    if fixture_root.is_symlink():
        raise ValueError(f"fixture root must be physical: {fixture_root}")
    for raw_path in task.fixture_paths:
        portable = PurePosixPath(raw_path)
        if portable.is_absolute() or ".." in portable.parts or "\\" in raw_path:
            raise ValueError(f"{task.path}: fixture escapes suite: {raw_path}")
        candidate = fixture_root.joinpath(*portable.parts)
        cursor = fixture_root
        for part in portable.parts:
            cursor /= part
            if cursor.is_symlink():
                raise ValueError(f"{task.path}: fixture traverses symlink: {raw_path}")
        candidate.resolve(strict=True).relative_to(fixture_root.resolve(strict=True))
        if not candidate.is_file():
            raise ValueError(f"{task.path}: fixture must be a regular file: {raw_path}")
    if fixture_root.exists():
        for fixture in sorted(fixture_root.rglob("*")):
            if "__pycache__" in fixture.parts:
                continue
            if fixture.is_symlink():
                raise ValueError(f"fixture must be physical: {fixture}")
            if fixture.is_file() and _GENERIC_HELLO.search(
                fixture.read_text(encoding="utf-8")
            ):
                raise ValueError(f"generic hello fixture is forbidden: {fixture}")
    task.path.resolve(strict=True).relative_to(root)


def _require_eval_suites(
    root: Path,
    records: tuple[SkillRecord, ...],
    seen_ids: set[str],
    seen_prompts: set[str],
) -> None:
    eval_root = root / "evals"
    if eval_root.is_symlink() or not eval_root.is_dir():
        raise ValueError(f"eval root must be a physical directory: {eval_root}")
    for record in records:
        directory = eval_root / record.name
        suite = load_eval_suite(directory)
        expected_directory = f"../../skills/{record.category.value}/{record.name}"
        if (
            suite.skill != record.name
            or suite.required_skills != (record.name,)
            or suite.skill_directories != (expected_directory,)
        ):
            raise ValueError(f"{suite.path}: suite must bind exactly {record.name}")
        raw_config = suite.path.read_text(encoding="utf-8")
        if "relevant_content" in raw_config:
            raise ValueError(
                f"{suite.path}: generic relevant_content grader is forbidden"
            )
        prompt_graders = tuple(
            grader for grader in suite.graders if grader.kind == "prompt"
        )
        if not any(
            grader.prompt is not None
            and record.name.casefold() in grader.prompt.casefold()
            and grader.name is not None
            and record.name.casefold() in grader.name.casefold()
            for grader in prompt_graders
        ):
            raise ValueError(f"{suite.path}: skill-specific prompt grader is required")
        behavior = tuple(
            grader for grader in suite.graders if grader.kind == "behavior"
        )
        if (
            suite.timeout_seconds is None
            or suite.timeout_seconds <= 0
            or len(behavior) != 1
            or behavior[0].max_duration_ms is None
            or behavior[0].max_duration_ms <= 0
            or behavior[0].max_duration_ms >= suite.timeout_seconds * 1000
        ):
            raise ValueError(f"{suite.path}: one bounded behavior grader is required")
        roles = tuple(task.role for task in suite.tasks)
        if len(suite.tasks) != len(EvalRole) or frozenset(roles) != frozenset(EvalRole):
            raise ValueError(f"{suite.path}: task roles must equal {tuple(EvalRole)}")
        frontmatter = Catalog._frontmatter(record.directory / "SKILL.md")
        description = require_description(frontmatter["description"])
        for task in suite.tasks:
            _require_task(
                root,
                directory,
                task,
                seen_ids,
                seen_prompts,
                description,
            )


def _require_local_links(root: Path, directory: Path, markdown: Path) -> None:
    text = _FENCED_CODE.sub("", markdown.read_text(encoding="utf-8"))
    for raw_target in _LINK.findall(text):
        target = raw_target.strip().split(maxsplit=1)[0]
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if not clean or ("/" not in clean and "." not in clean):
            continue
        portable = PurePosixPath(clean)
        if portable.is_absolute() or "\\" in clean:
            raise ValueError(
                f"{markdown}: local reference escapes bundle: {raw_target}"
            )
        candidate = markdown.parent.joinpath(*portable.parts)
        candidate.resolve(strict=True).relative_to(directory.resolve(strict=True))
        candidate.relative_to(root)


def _require_skill(root: Path, catalog: Catalog, record: SkillRecord) -> None:
    directory = record.directory
    catalog.digest_tree(directory)
    skill_file = directory / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = Catalog._frontmatter(skill_file)
    require_description(frontmatter["description"])
    if record.category is SkillCategory.PROJECT_WIDE or (
        record.category.conditional and record.route == "project"
    ):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and NON_PORTABLE_PROJECT_REFERENCE.search(
                path.read_text(encoding="utf-8")
            ):
                raise ValueError(f"project-distributed skill is not portable: {path}")
    policy = catalog.policy(record.name)
    token_estimate = bpe_tokens(skill_file, root)
    if token_estimate > policy.max_tokens:
        raise ValueError(f"{skill_file}: {token_estimate} > {policy.max_tokens} tokens")
    lines = len(text.splitlines())
    if lines > policy.max_lines:
        raise ValueError(f"{skill_file}: {lines} > {policy.max_lines} lines")
    markdown = (skill_file, *sorted(directory.rglob("*.md")))
    for path in dict.fromkeys(markdown):
        _require_local_links(root, directory, path)


def _require_no_orphan_directories(root: Path, *, require_all_categories: bool) -> None:
    skills_root = root / "skills"
    if not skills_root.exists() and not skills_root.is_symlink():
        if require_all_categories:
            raise ValueError(f"skills root must be a physical directory: {skills_root}")
        return
    if skills_root.is_symlink() or not skills_root.is_dir():
        raise ValueError(f"skills root must be a physical directory: {skills_root}")
    category_roots = {
        category.value: skills_root / category.value for category in SkillCategory
    }
    if require_all_categories:
        for category_root in category_roots.values():
            if category_root.is_symlink() or not category_root.is_dir():
                raise ValueError(
                    f"skill category must be a physical directory: {category_root}"
                )
    for category_root in sorted(skills_root.iterdir()):
        if category_root.name not in category_roots:
            if category_root.is_symlink() or category_root.is_dir():
                raise ValueError(f"unknown skill category: {category_root}")
            if category_root.is_file():
                continue
            raise ValueError(f"unsupported skill root entry: {category_root}")
        if category_root.is_symlink() or not category_root.is_dir():
            raise ValueError(
                f"skill category must be a physical directory: {category_root}"
            )
        for directory in sorted(category_root.iterdir()):
            if not directory.is_dir() or directory.is_symlink():
                raise ValueError(
                    f"skill entry must be a physical directory: {directory}"
                )
            if not (directory / "SKILL.md").is_file():
                raise ValueError(f"skill directory has no SKILL.md: {directory}")


def _validate_skill_catalog(
    catalog: Catalog,
    *,
    require_all_categories: bool,
    seen_ids: set[str],
    seen_prompts: set[str],
) -> None:
    root = catalog.root
    _require_no_orphan_directories(root, require_all_categories=require_all_categories)
    records = catalog.records()
    if not records:
        return
    validate_skill_metadata(root)
    for record in records:
        _require_skill(root, catalog, record)
    _require_eval_suites(root, records, seen_ids, seen_prompts)


def validate_skill_catalogs(central: Catalog, project: Catalog | None = None) -> None:
    """Validate central and optional project-local skills as one publication input."""

    if project is not None:
        if not project.project_local:
            raise ValueError("project skill catalog must be project-local")
        central_names = {record.name for record in central.records()}
        for record in project.records():
            if record.name in central_names:
                raise ValueError(f"central/local skill name collision: {record.name}")
        central_digests = {
            central.digest_tree(record.directory): record.name
            for record in central.records()
        }
        for record in project.records():
            digest = project.digest_tree(record.directory)
            if digest in central_digests:
                raise ValueError(
                    "central/local skill source digest collision: "
                    f"{central_digests[digest]}, {record.name}"
                )

    seen_ids: set[str] = set()
    seen_prompts: set[str] = set()
    _validate_skill_catalog(
        central,
        require_all_categories=True,
        seen_ids=seen_ids,
        seen_prompts=seen_prompts,
    )
    if project is not None:
        _validate_skill_catalog(
            project,
            require_all_categories=False,
            seen_ids=seen_ids,
            seen_prompts=seen_prompts,
        )


def validate(
    catalog: Catalog,
    model: str,
    commands: tuple[CommandSpec, ...],
    agents: tuple[AgentProfile, ...],
    rules: tuple[RuleSpec, ...],
) -> None:
    """Validate the complete authority or raise on the first defect."""

    if not model or model != model.strip():
        raise ValueError("validated Waza model must be non-empty and trimmed")
    if not commands:
        raise ValueError("command inventory is empty")
    if not agents:
        raise ValueError("agent inventory is empty")
    if not rules:
        raise ValueError("rule inventory is empty")
    validate_skill_catalogs(catalog)


__all__ = ("require_description", "validate", "validate_skill_catalogs")
