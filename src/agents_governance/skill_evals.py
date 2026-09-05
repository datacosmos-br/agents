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
        "description",
        "graders",
        "version",
    }
)
_DEFAULT_FIELDS = frozenset(
    {"behavior_grader", "execution", "metric", "tasks", "version"}
)
_EXECUTION_FIELDS = frozenset(
    {
        "fail_fast",
        "parallel",
        "retry_attempts",
        "timeout_seconds",
        "trials_per_task",
    }
)
_GRADER_FIELDS = frozenset({"config", "name", "type"})
_INPUT_FIELDS = frozenset({"files", "prompt"})
_INPUT_FILE_FIELDS = frozenset({"path"})
_METRIC_FIELDS = frozenset({"description", "name", "threshold", "weight"})
_EXPECTED_FIELDS = frozenset({"outcomes", "output_contains", "output_not_contains"})
_OUTCOME_FIELDS = frozenset({"type"})
_TASK_FIELDS = frozenset({"description", "expected", "id", "inputs", "name", "tags"})
_TASK_ROLES = {
    "fail_closed": "tasks/edge-case.yaml",
    "happy_path": "tasks/basic-usage.yaml",
    "non_trigger": "tasks/should-not-trigger.yaml",
}


def _trimmed_text(value: object, context: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise TypeError(f"{context} must be non-empty trimmed text")
    return value


def _nonempty_text(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{context} must be non-empty text")
    return value


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


def _task_files(suite: Path, declared: dict[str, str]) -> tuple[tuple[Path, str], ...]:
    task_root = suite / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"evaluation task root must be physical: {task_root}")
    task_files = tuple(sorted(task_root.iterdir()))
    expected = {Path(relative).name for relative in declared.values()}
    if {path.name for path in task_files} != expected:
        raise ValueError(f"{task_root}: tasks must be exactly {sorted(expected)}")
    for path in task_files:
        if path.is_symlink() or not path.is_file() or path.suffix != ".yaml":
            raise ValueError(f"evaluation tasks support only physical YAML: {path}")
    return tuple((suite / relative, role) for role, relative in declared.items())


def _audit_inputs(path: Path, value: object, fixtures: set[Path]) -> str:
    inputs = cast_mapping(value, f"{path}: inputs")
    fields = frozenset(inputs)
    if "prompt" not in fields or not fields <= _INPUT_FIELDS:
        raise ValueError(f"{path}: inputs supports only prompt and optional files")
    prompt = _nonempty_text(inputs["prompt"], f"{path}: inputs.prompt")
    raw_files = inputs.get("files")
    if raw_files is None:
        return prompt
    if not isinstance(raw_files, list) or not raw_files:
        raise TypeError(f"{path}: inputs.files must be a non-empty array")
    fixture_root = path.parent.parent / "fixtures"
    for index, raw_file in enumerate(raw_files):
        context = f"{path}: inputs.files[{index}]"
        record = cast_mapping(raw_file, context)
        require_exact_fields(record, _INPUT_FILE_FIELDS, context)
        relative = Path(_trimmed_text(record["path"], f"{context}.path"))
        if relative.is_absolute():
            raise ValueError(f"{context}.path must be relative to fixtures")
        resolved = (fixture_root / relative).resolve(strict=True)
        owner = fixture_root.resolve(strict=True)
        if (
            not resolved.is_relative_to(owner)
            or resolved.is_symlink()
            or not resolved.is_file()
        ):
            raise ValueError(f"{context}.path must resolve to a physical fixture")
        fixtures.add(resolved)
    return prompt


def _audit_expected(path: Path, value: object, role: str) -> None:
    expected = cast_mapping(value, f"{path}: expected")
    fields = frozenset(expected)
    if not fields or not fields <= _EXPECTED_FIELDS:
        raise ValueError(f"{path}: expected contains unsupported or no assertions")
    if not fields & {"output_contains", "output_not_contains"}:
        raise ValueError(f"{path}: expected requires a material output assertion")
    if role in {"happy_path", "fail_closed"} and "output_contains" not in fields:
        raise ValueError(f"{path}: {role} requires output_contains")
    if role in {"fail_closed", "non_trigger"} and "output_not_contains" not in fields:
        raise ValueError(f"{path}: {role} requires output_not_contains")
    for field in ("output_contains", "output_not_contains"):
        if field in expected:
            string_array(expected[field], f"{path}: expected.{field}")
    outcomes = expected.get("outcomes")
    if outcomes is not None:
        if not isinstance(outcomes, list) or not outcomes:
            raise TypeError(f"{path}: expected.outcomes must be a non-empty array")
        for index, raw_outcome in enumerate(outcomes):
            context = f"{path}: expected.outcomes[{index}]"
            outcome = cast_mapping(raw_outcome, context)
            require_exact_fields(outcome, _OUTCOME_FIELDS, context)
            if outcome["type"] != "task_completed":
                raise ValueError(f"{context}.type must equal 'task_completed'")


def _audit_task(
    path: Path,
    role: str,
    identifiers: set[str],
    prompts: set[str],
    fixtures: set[Path],
) -> None:
    task = _mapping(path)
    require_exact_fields(task, _TASK_FIELDS, str(path))
    identifier = task["id"]
    identifier = _trimmed_text(identifier, f"{path}: id")
    if identifier in identifiers:
        raise ValueError(f"evaluation task id is duplicated: {identifier}")
    identifiers.add(identifier)
    for field in ("name", "description"):
        _trimmed_text(task[field], f"{path}: {field}")
    string_array(task["tags"], f"{path}: tags")
    prompt = _audit_inputs(path, task["inputs"], fixtures)
    if prompt in prompts:
        raise ValueError(f"{path}: evaluation prompt is duplicated")
    prompts.add(prompt)
    _audit_expected(path, task["expected"], role)


def _audit_graders(source: Path, value: object, skill: SkillRecord) -> None:
    if not isinstance(value, list) or len(value) != 1:
        raise TypeError(f"{source}: graders must contain one prompt contract")
    prompt_grader = cast_mapping(value[0], f"{source}: graders[0]")
    require_exact_fields(prompt_grader, _GRADER_FIELDS, f"{source}: graders[0]")
    prompt_name = _trimmed_text(prompt_grader["name"], f"{source}: graders[0].name")
    if (
        prompt_grader["type"] != "prompt"
        or not prompt_name.startswith(f"{skill.name}-")
        or not prompt_name.endswith("-contract")
    ):
        raise ValueError(f"{source}: first grader must own the skill prompt contract")
    prompt_config = cast_mapping(
        prompt_grader["config"], f"{source}: graders[0].config"
    )
    require_exact_fields(
        prompt_config, frozenset({"prompt"}), f"{source}: graders[0].config"
    )
    _nonempty_text(prompt_config["prompt"], f"{source}: graders[0].config.prompt")


def _audit_defaults(path: Path) -> dict[str, str]:
    defaults = _mapping(path)
    require_exact_fields(defaults, _DEFAULT_FIELDS, str(path))
    if defaults["version"] != 1:
        raise ValueError(f"{path}: version must equal 1")
    execution = cast_mapping(defaults["execution"], f"{path}: execution")
    require_exact_fields(execution, _EXECUTION_FIELDS, f"{path}: execution")
    if execution["trials_per_task"] != 1:
        raise ValueError(f"{path}: trials_per_task must equal 1")
    timeout_seconds = execution["timeout_seconds"]
    if type(timeout_seconds) is not int or not 0 < timeout_seconds <= 60:
        raise ValueError(f"{path}: timeout_seconds must be in 1..60")
    if execution["retry_attempts"] != 0:
        raise ValueError(f"{path}: retry_attempts must equal 0")
    if execution["parallel"] is not False or execution["fail_fast"] is not True:
        raise ValueError(f"{path}: execution must be serial and fail fast")
    metric = cast_mapping(defaults["metric"], f"{path}: metric")
    require_exact_fields(metric, _METRIC_FIELDS, f"{path}: metric")
    if metric["name"] != "behavior_quality":
        raise ValueError(f"{path}: metric must equal behavior_quality")
    if metric["weight"] != 1.0 or metric["threshold"] != 1.0:
        raise ValueError(f"{path}: metric weight and threshold must equal 1.0")
    _trimmed_text(metric["description"], f"{path}: metric.description")
    behavior = cast_mapping(defaults["behavior_grader"], f"{path}: behavior_grader")
    require_exact_fields(behavior, _GRADER_FIELDS, f"{path}: behavior_grader")
    if behavior["type"] != "behavior" or behavior["name"] != "bounded_execution":
        raise ValueError(f"{path}: behavior_grader must be bounded_execution")
    behavior_config = cast_mapping(
        behavior["config"], f"{path}: behavior_grader.config"
    )
    require_exact_fields(
        behavior_config,
        frozenset({"max_duration_ms"}),
        f"{path}: behavior_grader.config",
    )
    duration = behavior_config["max_duration_ms"]
    if type(duration) is not int or duration <= 0 or duration >= timeout_seconds * 1000:
        raise ValueError(f"{path}: max_duration_ms must be positive and below timeout")
    tasks = cast_mapping(defaults["tasks"], f"{path}: tasks")
    require_exact_fields(tasks, frozenset(_TASK_ROLES), f"{path}: tasks")
    parsed = {
        role: _trimmed_text(tasks[role], f"{path}: tasks.{role}")
        for role in sorted(_TASK_ROLES)
    }
    if parsed != _TASK_ROLES:
        raise ValueError(f"{path}: task role paths are not canonical")
    return parsed


def _audit_suite(
    suite: Path,
    skill: SkillRecord,
    identifiers: set[str],
    prompts: set[str],
    task_roles: dict[str, str],
) -> None:
    _physical_tree(suite)
    children = {path.name for path in suite.iterdir()}
    if not {"suite.yaml", "tasks"} <= children or not children <= {
        "fixtures",
        "suite.yaml",
        "tasks",
    }:
        raise ValueError(f"{suite}: unsupported or missing suite resources")
    source = suite / "suite.yaml"
    evaluation = _mapping(source)
    require_exact_fields(evaluation, _EVAL_FIELDS, str(source))
    version = _trimmed_text(evaluation["version"], f"{source}: version")
    version_parts = version.split(".")
    if (
        len(version_parts) != 2
        or not all(part.isdigit() for part in version_parts)
        or int(version_parts[0]) < 1
    ):
        raise ValueError(f"{source}: version must be a positive major.minor value")
    _trimmed_text(evaluation["description"], f"{source}: description")
    _audit_graders(source, evaluation["graders"], skill)
    fixtures: set[Path] = set()
    for task, role in _task_files(suite, task_roles):
        _audit_task(task, role, identifiers, prompts, fixtures)
    fixture_root = suite / "fixtures"
    physical_fixtures = (
        {
            path.resolve(strict=True)
            for path in fixture_root.rglob("*")
            if path.is_file()
        }
        if fixture_root.exists()
        else set()
    )
    if fixtures != physical_fixtures:
        raise ValueError(f"{suite}: fixtures must exactly equal referenced files")


def audit_skill_evals(root: Path, skills: tuple[SkillRecord, ...]) -> None:
    """Require one complete physical semantic evaluation suite per skill."""

    repository = root.resolve(strict=True)
    task_roles = _audit_defaults(repository / "config" / "evals.json")
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
    prompts: set[str] = set()
    for suite in entries:
        skill = by_name[suite.name]
        _audit_suite(suite, skill, identifiers, prompts, task_roles)


__all__ = ("audit_skill_evals",)
