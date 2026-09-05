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
        "metrics",
        "name",
        "schema_version",
        "skill",
        "tasks",
        "version",
    }
)
_CONFIG_FIELDS = frozenset(
    {
        "fail_fast",
        "parallel",
        "required_skills",
        "retry_attempts",
        "skill_directories",
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
_TASK_FILES = frozenset(
    {"basic-usage.yaml", "edge-case.yaml", "should-not-trigger.yaml"}
)


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


def _task_files(suite: Path, declared: object) -> tuple[Path, ...]:
    if string_array(declared, f"{suite / 'suite.yaml'}: tasks") != ("tasks/*.yaml",):
        raise ValueError(f"{suite / 'suite.yaml'}: tasks must equal ['tasks/*.yaml']")
    task_root = suite / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"evaluation task root must be physical: {task_root}")
    task_files = tuple(sorted(task_root.iterdir()))
    if {path.name for path in task_files} != _TASK_FILES:
        raise ValueError(f"{task_root}: tasks must be exactly {sorted(_TASK_FILES)}")
    for path in task_files:
        if path.is_symlink() or not path.is_file() or path.suffix != ".yaml":
            raise ValueError(f"evaluation tasks support only physical YAML: {path}")
    return task_files


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


def _audit_expected(path: Path, value: object) -> None:
    expected = cast_mapping(value, f"{path}: expected")
    fields = frozenset(expected)
    if not fields or not fields <= _EXPECTED_FIELDS:
        raise ValueError(f"{path}: expected contains unsupported or no assertions")
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
    _audit_expected(path, task["expected"])


def _audit_graders(
    source: Path, value: object, skill: SkillRecord, timeout_seconds: int
) -> None:
    if not isinstance(value, list) or len(value) != 2:
        raise TypeError(f"{source}: graders must contain prompt and behavior")
    prompt_grader = cast_mapping(value[0], f"{source}: graders[0]")
    behavior_grader = cast_mapping(value[1], f"{source}: graders[1]")
    require_exact_fields(prompt_grader, _GRADER_FIELDS, f"{source}: graders[0]")
    require_exact_fields(behavior_grader, _GRADER_FIELDS, f"{source}: graders[1]")
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
    if (
        behavior_grader["type"] != "behavior"
        or behavior_grader["name"] != "bounded_execution"
    ):
        raise ValueError(f"{source}: second grader must be bounded_execution behavior")
    behavior_config = cast_mapping(
        behavior_grader["config"], f"{source}: graders[1].config"
    )
    require_exact_fields(
        behavior_config,
        frozenset({"max_duration_ms"}),
        f"{source}: graders[1].config",
    )
    duration = behavior_config["max_duration_ms"]
    if type(duration) is not int or duration <= 0 or duration >= timeout_seconds * 1000:
        raise ValueError(
            f"{source}: bounded execution duration must be positive and below timeout"
        )


def _audit_suite(
    suite: Path,
    skill: SkillRecord,
    identifiers: set[str],
    prompts: set[str],
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
    if evaluation["skill"] != skill.name:
        raise ValueError(f"{source}: skill must equal {skill.name!r}")
    if evaluation["name"] != f"{skill.name}-eval":
        raise ValueError(f"{source}: name must equal {skill.name!r}-eval")
    if evaluation["schema_version"] != 1:
        raise ValueError(f"{source}: schema_version must equal 1")
    version = _trimmed_text(evaluation["version"], f"{source}: version")
    version_parts = version.split(".")
    if (
        len(version_parts) != 2
        or not all(part.isdigit() for part in version_parts)
        or int(version_parts[0]) < 1
    ):
        raise ValueError(f"{source}: version must be a positive major.minor value")
    _trimmed_text(evaluation["description"], f"{source}: description")
    config = cast_mapping(evaluation["config"], f"{source}: config")
    require_exact_fields(config, _CONFIG_FIELDS, f"{source}: config")
    for field in ("trials_per_task", "timeout_seconds"):
        value = config[field]
        if type(value) is not int or value <= 0:
            raise TypeError(f"{source}: config.{field} must be a positive integer")
    if config["retry_attempts"] != 0:
        raise ValueError(f"{source}: config.retry_attempts must equal 0")
    if config["parallel"] is not False or config["fail_fast"] is not True:
        raise ValueError(
            f"{source}: config must disable parallel execution and fail fast"
        )
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
    metrics = evaluation["metrics"]
    if not isinstance(metrics, list) or len(metrics) != 1:
        raise TypeError(f"{source}: metrics must contain behavior_quality")
    total_weight = 0.0
    for index, raw_metric in enumerate(metrics):
        metric = cast_mapping(raw_metric, f"{source}: metrics[{index}]")
        require_exact_fields(metric, _METRIC_FIELDS, f"{source}: metrics[{index}]")
        name = metric["name"]
        description = metric["description"]
        if name != "behavior_quality":
            raise ValueError(f"{source}: metric must equal behavior_quality")
        _trimmed_text(description, f"{source}: metrics[{index}].description")
        weight = metric["weight"]
        threshold = metric["threshold"]
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or weight <= 0
        ):
            raise TypeError(f"{source}: metrics[{index}].weight must be positive")
        if threshold != 1.0:
            raise ValueError(f"{source}: metrics[{index}].threshold must equal 1.0")
        total_weight += float(weight)
    if abs(total_weight - 1.0) > 1e-9:
        raise ValueError(f"{source}: metric weights must total 1.0")
    timeout_seconds = config["timeout_seconds"]
    assert isinstance(timeout_seconds, int)
    _audit_graders(source, evaluation["graders"], skill, timeout_seconds)
    fixtures: set[Path] = set()
    for task in _task_files(suite, evaluation["tasks"]):
        _audit_task(task, identifiers, prompts, fixtures)
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
        _audit_suite(suite, skill, identifiers, prompts)


__all__ = ("audit_skill_evals",)
