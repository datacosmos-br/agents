"""Validate provider-neutral skill evaluation resources."""

from __future__ import annotations

import stat
from dataclasses import dataclass
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

_EVAL_FIELDS = frozenset({"description", "prompt", "version"})
_REQUIRED_EVAL_FIELDS = frozenset({"description", "prompt"})
_DEFAULT_FIELDS = frozenset(
    {
        "behavior_grader",
        "default_suite_version",
        "execution",
        "metric",
        "tasks",
        "version",
        "waza_schema_version",
    }
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
_EXPECTED_FIELDS = frozenset({"output_contains", "output_not_contains"})
_TASK_FIELDS = frozenset({"description", "expected", "id", "inputs", "name", "tags"})
_TASK_ROLES = {
    "fail_closed": "tasks/edge-case.yaml",
    "happy_path": "tasks/basic-usage.yaml",
    "non_trigger": "tasks/should-not-trigger.yaml",
}


@dataclass(frozen=True)
class EvalExecutionPolicy:
    """Canonical execution policy for every semantic suite."""

    trials_per_task: int
    timeout_seconds: int
    parallel: bool
    retry_attempts: int
    fail_fast: bool


@dataclass(frozen=True)
class EvalMetricPolicy:
    """Canonical strict metric projected into every Waza suite."""

    name: str
    weight: float
    threshold: float
    description: str


@dataclass(frozen=True)
class EvalBehaviorGraderPolicy:
    """Canonical bounded-execution grader projected into every Waza suite."""

    type: str
    name: str
    max_duration_ms: int


@dataclass(frozen=True)
class EvalPolicy:
    """One immutable owner for shared semantic evaluation policy."""

    version: int
    default_suite_version: str
    waza_schema_version: str
    execution: EvalExecutionPolicy
    metric: EvalMetricPolicy
    behavior_grader: EvalBehaviorGraderPolicy
    tasks: tuple[tuple[str, str], ...]

    @property
    def task_glob(self) -> str:
        """Derive Waza's glob from the canonical task paths."""

        paths = tuple(Path(path) for _, path in self.tasks)
        return (paths[0].parent / f"*{paths[0].suffix}").as_posix()

    @property
    def task_suffix(self) -> str:
        """Return the validated common task suffix."""

        return Path(self.tasks[0][1]).suffix


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
    # One parse, through LibYAML. The node carries the duplicate-key evidence and
    # the document is constructed from that same node: composing with the
    # pure-Python loader and then calling ``safe_load`` parsed every evaluation
    # file twice with the slowest available parser, which is what made loading
    # the governance bundle take ~15s in every consumer process.
    loader = yaml.CSafeLoader(source)
    try:
        node = loader.get_single_node()
        if not isinstance(node, MappingNode):
            raise TypeError(f"evaluation resource must be a mapping: {path}")
        duplicate = detect_duplicate_key(node)
        if duplicate is not None:
            raise ValueError(f"{path}: evaluation key is duplicated: {duplicate}")
        loaded = loader.construct_document(node)
    finally:
        loader.dispose()
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


def _task_files(
    suite: Path, declared: tuple[tuple[str, str], ...]
) -> tuple[tuple[Path, str], ...]:
    task_root = suite / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"evaluation task root must be physical: {task_root}")
    task_files = tuple(sorted(task_root.iterdir()))
    expected = {Path(relative).name for _, relative in declared}
    if {path.name for path in task_files} != expected:
        raise ValueError(f"{task_root}: tasks must be exactly {sorted(expected)}")
    for path in task_files:
        if path.is_symlink() or not path.is_file() or path.suffix != ".yaml":
            raise ValueError(f"evaluation tasks support only physical YAML: {path}")
    return tuple((suite / relative, role) for role, relative in declared)


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
    if role in {"happy_path", "fail_closed"} and "output_contains" not in fields:
        raise ValueError(f"{path}: {role} requires output_contains")
    if role in {"fail_closed", "non_trigger"} and "output_not_contains" not in fields:
        raise ValueError(f"{path}: {role} requires output_not_contains")
    for field in sorted(fields):
        string_array(expected[field], f"{path}: expected.{field}")


def _audit_task(
    path: Path,
    role: str,
    identifiers: set[str],
    prompts: set[str],
    fixtures: set[Path],
) -> None:
    task = _mapping(path)
    require_exact_fields(task, _TASK_FIELDS, str(path))
    identifier = _trimmed_text(task["id"], f"{path}: id")
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


def _suite_version(value: object, context: str) -> str:
    version = _trimmed_text(value, context)
    parts = version.split(".")
    if (
        len(parts) != 2
        or not all(part.isdigit() for part in parts)
        or int(parts[0]) < 1
    ):
        raise ValueError(f"{context} must be a positive major.minor value")
    return version


def _audit_defaults(path: Path) -> EvalPolicy:
    defaults = _mapping(path)
    require_exact_fields(defaults, _DEFAULT_FIELDS, str(path))
    if defaults["version"] != 1:
        raise ValueError(f"{path}: version must equal 1")
    default_version = _suite_version(
        defaults["default_suite_version"], f"{path}: default_suite_version"
    )
    waza_schema_version = _trimmed_text(
        defaults["waza_schema_version"], f"{path}: waza_schema_version"
    )
    if waza_schema_version != "1.2":
        raise ValueError(f"{path}: waza_schema_version must equal 1.2")
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
    metric_description = _trimmed_text(
        metric["description"], f"{path}: metric.description"
    )
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
    parsed_tasks = tuple(
        (role, _trimmed_text(tasks[role], f"{path}: tasks.{role}"))
        for role in sorted(_TASK_ROLES)
    )
    if dict(parsed_tasks) != _TASK_ROLES:
        raise ValueError(f"{path}: task role paths are not canonical")
    paths = tuple(Path(relative) for _, relative in parsed_tasks)
    if (
        len({item.parent for item in paths}) != 1
        or len({item.suffix for item in paths}) != 1
    ):
        raise ValueError(f"{path}: task paths require one directory and suffix")
    return EvalPolicy(
        version=1,
        default_suite_version=default_version,
        waza_schema_version=waza_schema_version,
        execution=EvalExecutionPolicy(
            trials_per_task=1,
            timeout_seconds=timeout_seconds,
            parallel=False,
            retry_attempts=0,
            fail_fast=True,
        ),
        metric=EvalMetricPolicy(
            name="behavior_quality",
            weight=1.0,
            threshold=1.0,
            description=metric_description,
        ),
        behavior_grader=EvalBehaviorGraderPolicy(
            type="behavior",
            name="bounded_execution",
            max_duration_ms=duration,
        ),
        tasks=parsed_tasks,
    )


def _audit_suite(
    suite: Path,
    identifiers: set[str],
    prompts: set[str],
    policy: EvalPolicy,
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
    fields = frozenset(evaluation)
    if not _REQUIRED_EVAL_FIELDS <= fields or not fields <= _EVAL_FIELDS:
        raise ValueError(
            f"{source}: fields must be description, prompt, and optional version"
        )
    _trimmed_text(evaluation["description"], f"{source}: description")
    _nonempty_text(evaluation["prompt"], f"{source}: prompt")
    version = _suite_version(
        evaluation.get("version", policy.default_suite_version), f"{source}: version"
    )
    if "version" in evaluation and version == policy.default_suite_version:
        raise ValueError(f"{source}: default version must be omitted")
    fixtures: set[Path] = set()
    for task, role in _task_files(suite, policy.tasks):
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


def audit_skill_evals(root: Path, skills: tuple[SkillRecord, ...]) -> EvalPolicy:
    """Require one complete physical semantic evaluation suite per skill."""

    repository = root.resolve(strict=True)
    policy = _audit_defaults(repository / "config" / "evals.json")
    eval_root = repository / "evals"
    if eval_root.is_symlink() or not eval_root.is_dir():
        raise ValueError(f"skill evaluation root must be physical: {eval_root}")
    entries = tuple(sorted(eval_root.iterdir(), key=lambda path: path.name))
    if any(path.is_symlink() or not path.is_dir() for path in entries):
        raise ValueError(
            f"skill evaluation root supports only physical directories: {eval_root}"
        )
    skill_names = {skill.name for skill in skills}
    if {path.name for path in entries} != skill_names:
        raise ValueError(
            "skill evaluation suites must exactly equal the skill inventory"
        )
    identifiers: set[str] = set()
    prompts: set[str] = set()
    for suite in entries:
        _audit_suite(suite, identifiers, prompts, policy)
    return policy


__all__ = ("EvalPolicy", "audit_skill_evals")
