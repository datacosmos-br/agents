"""Validate provider-neutral skill evaluation resources."""

from __future__ import annotations

import stat
from pathlib import Path

import yaml
from yaml.nodes import MappingNode

from .catalog import SkillRecord
from .frontmatter import (
    cast_mapping,
    detect_duplicate_key,
    require_exact_fields,
    string_array,
)

_EVAL_FIELDS = frozenset(
    {
        "config",
        "description",
        "graders",
        "name",
        "schemaVersion",
        "skill",
        "tasks",
        "version",
    }
)
_EVAL_FIELDS_WITH_METRICS = _EVAL_FIELDS | {"metrics"}
_TASK_FIELDS = frozenset({"description", "expected", "id", "inputs", "name", "tags"})


def _mapping(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"evaluation resource must be a physical file: {path}")
    source = path.read_text(encoding="utf-8")
    node = yaml.compose(source, Loader=yaml.SafeLoader)
    loaded = yaml.safe_load(source)
    if not isinstance(node, MappingNode):
        raise TypeError(f"evaluation resource must be a mapping: {path}")
    duplicate = detect_duplicate_key(node)
    if duplicate is not None:
        raise ValueError(f"{path}: evaluation key is duplicated: {duplicate}")
    return cast_mapping(loaded, str(path))


def _physical_tree(directory: Path) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f"evaluation suite must be a physical directory: {directory}")
    for path in sorted(directory.rglob("*")):
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"evaluation resource must be physical: {path}")
        if not stat.S_ISDIR(metadata.st_mode) and not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"unsupported evaluation resource type: {path}")


def _task_files(suite: Path, declared: object) -> tuple[Path, ...]:
    if string_array(declared, f"{suite / 'eval.yaml'}: tasks") != ("tasks/*.yaml",):
        raise ValueError(f"{suite / 'eval.yaml'}: tasks must equal ['tasks/*.yaml']")
    task_root = suite / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"evaluation task root must be physical: {task_root}")
    task_files = tuple(sorted(task_root.iterdir()))
    if not task_files:
        raise ValueError(f"evaluation task inventory is empty: {task_root}")
    for path in task_files:
        if path.is_symlink() or not path.is_file() or path.suffix != ".yaml":
            raise ValueError(f"evaluation tasks support only physical YAML: {path}")
    return task_files


def _audit_task(path: Path, identifiers: set[str]) -> None:
    task = _mapping(path)
    require_exact_fields(task, _TASK_FIELDS, str(path))
    identifier = task["id"]
    if (
        not isinstance(identifier, str)
        or not identifier
        or identifier != identifier.strip()
    ):
        raise TypeError(f"{path}: id must be a non-empty trimmed string")
    if identifier in identifiers:
        raise ValueError(f"evaluation task id is duplicated: {identifier}")
    identifiers.add(identifier)
    for field in ("name", "description"):
        value = task[field]
        if not isinstance(value, str) or not value or value != value.strip():
            raise TypeError(f"{path}: {field} must be a non-empty trimmed string")
    string_array(task["tags"], f"{path}: tags")
    inputs = cast_mapping(task["inputs"], f"{path}: inputs")
    prompt = inputs.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise TypeError(f"{path}: inputs.prompt must be non-empty text")
    expected = cast_mapping(task["expected"], f"{path}: expected")
    if not expected:
        raise ValueError(f"{path}: expected must not be empty")
    if "output_contains" in expected:
        string_array(
            expected["output_contains"],
            f"{path}: expected.output_contains",
            require_unique=False,
        )
    if "output_not_contains" in expected:
        string_array(
            expected["output_not_contains"],
            f"{path}: expected.output_not_contains",
            require_unique=False,
        )


def _audit_suite(suite: Path, skill: SkillRecord, identifiers: set[str]) -> None:
    _physical_tree(suite)
    source = suite / "eval.yaml"
    evaluation = _mapping(source)
    if frozenset(evaluation) not in {_EVAL_FIELDS, _EVAL_FIELDS_WITH_METRICS}:
        raise ValueError(f"{source}: unsupported evaluation fields")
    if evaluation["skill"] != skill.name:
        raise ValueError(f"{source}: skill must equal {skill.name!r}")
    if evaluation["name"] != f"{skill.name}-eval":
        raise ValueError(f"{source}: name must equal {skill.name!r}-eval")
    if evaluation["schemaVersion"] != "1.0":
        raise ValueError(f"{source}: schemaVersion must equal '1.0'")
    description = evaluation["description"]
    if (
        not isinstance(description, str)
        or not description
        or description != description.strip()
    ):
        raise TypeError(f"{source}: description must be non-empty trimmed text")
    config = cast_mapping(evaluation["config"], f"{source}: config")
    directories = string_array(
        config.get("skill_directories"), f"{source}: config.skill_directories"
    )
    if len(directories) != 1:
        raise ValueError(f"{source}: exactly one skill directory is required")
    resolved = (suite / directories[0]).resolve(strict=True)
    if resolved != skill.directory.resolve(strict=True):
        raise ValueError(f"{source}: skill directory does not resolve to its owner")
    if string_array(
        config.get("required_skills"), f"{source}: config.required_skills"
    ) != (skill.name,):
        raise ValueError(f"{source}: required_skills must contain only {skill.name!r}")
    graders = evaluation["graders"]
    if not isinstance(graders, list) or not graders:
        raise TypeError(f"{source}: graders must be a non-empty array")
    for task in _task_files(suite, evaluation["tasks"]):
        _audit_task(task, identifiers)


def audit_skill_evals(root: Path, skills: tuple[SkillRecord, ...]) -> None:
    """Require one complete physical semantic evaluation suite per skill."""

    repository = root.resolve(strict=True)
    eval_root = repository / "evals"
    if eval_root.is_symlink() or not eval_root.is_dir():
        raise ValueError(f"skill evaluation root must be physical: {eval_root}")
    entries = tuple(sorted(eval_root.iterdir(), key=lambda path: path.name))
    if any(path.is_symlink() or not path.is_dir() for path in entries):
        raise ValueError(
            f"skill evaluation root supports only physical directories: {eval_root}"
        )
    by_name = {skill.name: skill for skill in skills}
    if {path.name for path in entries} != set(by_name):
        raise ValueError(
            "skill evaluation suites must exactly equal the skill inventory"
        )
    identifiers: set[str] = set()
    for suite in entries:
        skill = by_name[suite.name]
        _audit_suite(suite, skill, identifiers)


__all__ = ("audit_skill_evals",)
