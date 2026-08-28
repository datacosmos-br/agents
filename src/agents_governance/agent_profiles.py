"""Typed validation for canonical, provider-neutral agent profiles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from .catalog import NON_PORTABLE_PROJECT_REFERENCE

_DISTRIBUTIONS = frozenset({"agent-wide", "project-wide"})
_ACTIVATIONS = frozenset(
    {"activation:always", "activation:detected", "activation:opt-in"}
)
_MODES = frozenset(
    {"mode:debug", "mode:execute", "mode:operate", "mode:plan", "mode:review"}
)
_RETIRED_SURFACES = frozenset({"dispatcher.md", "manifest.json"})
_PROMPT_DEFENSE_RULE = "rules/security/prompt-defense.md"
_INLINE_PROMPT_DEFENSE = "## Prompt Defense Baseline"


@dataclass(frozen=True)
class AgentProfile:
    """One validated, provider-neutral agent profile."""

    path: Path
    name: str
    description: str
    distribution: str
    tags: tuple[str, ...]
    rule_paths: tuple[str, ...]
    instructions: str


@dataclass(frozen=True)
class AgentProfileFinding:
    """One blocking agent-profile contract violation."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class AgentProfileAudit:
    """Validated profiles and every blocking finding discovered together."""

    profiles: tuple[AgentProfile, ...]
    findings: tuple[AgentProfileFinding, ...]


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


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _finding(path: str, code: str, message: str) -> AgentProfileFinding:
    return AgentProfileFinding(path, code, message)


def _tag_values(metadata: dict[str, object]) -> tuple[str, ...]:
    container = metadata.get("metadata")
    if not isinstance(container, dict):
        raise TypeError("metadata must be a mapping")
    raw = container.get("aihub.tags")
    if not isinstance(raw, str):
        raise TypeError("metadata.aihub.tags must be a JSON string")
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("metadata.aihub.tags must contain valid JSON") from error
    if not isinstance(loaded, list) or not all(
        isinstance(item, str) and item and not any(char.isspace() for char in item)
        for item in loaded
    ):
        raise TypeError("metadata.aihub.tags must be a JSON array of non-empty tags")
    return tuple(loaded)


def _one_tag(tags: tuple[str, ...], prefix: str) -> tuple[str, ...]:
    return tuple(tag for tag in tags if tag.startswith(prefix))


def _tag_findings(
    relative: str, distribution: str, tags: tuple[str, ...]
) -> list[AgentProfileFinding]:
    findings: list[AgentProfileFinding] = []
    if len(tags) != len(set(tags)):
        findings.append(_finding(relative, "agent-profile-tags", "tags must be unique"))
    if tags != tuple(sorted(tags)):
        findings.append(_finding(relative, "agent-profile-tags", "tags must be sorted"))

    activations = _one_tag(tags, "activation:")
    modes = _one_tag(tags, "mode:")
    roles = _one_tag(tags, "role:")
    detectors = _one_tag(tags, "detect:")
    if len(activations) != 1 or activations[0] not in _ACTIVATIONS:
        findings.append(
            _finding(
                relative,
                "agent-profile-activation",
                "exactly one supported activation tag is required",
            )
        )
    if len(modes) != 1 or modes[0] not in _MODES:
        findings.append(
            _finding(
                relative,
                "agent-profile-mode",
                "exactly one supported mode tag is required",
            )
        )
    if len(roles) != 1 or roles[0] == "role:":
        findings.append(
            _finding(
                relative,
                "agent-profile-role",
                "exactly one non-empty role tag is required",
            )
        )
    activation = activations[0] if len(activations) == 1 else None
    if distribution == "agent-wide" and activation != "activation:always":
        findings.append(
            _finding(
                relative,
                "agent-profile-distribution",
                "agent-wide profiles require activation:always",
            )
        )
    if distribution == "project-wide" and activation == "activation:always":
        findings.append(
            _finding(
                relative,
                "agent-profile-distribution",
                "project-wide profiles cannot use activation:always",
            )
        )
    if activation == "activation:detected" and not detectors:
        findings.append(
            _finding(
                relative,
                "agent-profile-detector",
                "detected profiles require at least one detect tag",
            )
        )
    if activation != "activation:detected" and detectors:
        findings.append(
            _finding(
                relative,
                "agent-profile-detector",
                "detect tags are allowed only with activation:detected",
            )
        )
    return findings


def _candidate_paths(
    root: Path, agents: Path
) -> tuple[list[Path], list[AgentProfileFinding]]:
    candidates: list[Path] = []
    findings: list[AgentProfileFinding] = []
    for path in sorted(agents.rglob("*")):
        relative = _relative(root, path)
        parts = path.relative_to(agents).parts
        if len(parts) == 1:
            if path.name in _RETIRED_SURFACES:
                findings.append(
                    _finding(
                        relative,
                        "agent-profile-retired-surface",
                        "retired manifest/dispatcher surface is forbidden",
                    )
                )
            elif path.is_symlink():
                findings.append(
                    _finding(
                        relative, "agent-profile-symlink", "agent path is a symlink"
                    )
                )
            elif not path.is_dir() or path.name not in _DISTRIBUTIONS:
                findings.append(
                    _finding(
                        relative,
                        "agent-profile-path",
                        "profiles must use agents/{agent-wide,project-wide}/<slug>.md",
                    )
                )
            continue

        if parts[0] not in _DISTRIBUTIONS:
            continue
        if len(parts) != 2 or path.suffix != ".md":
            findings.append(
                _finding(
                    relative,
                    "agent-profile-path",
                    "profiles must use agents/{agent-wide,project-wide}/<slug>.md",
                )
            )
            continue
        if path.is_symlink():
            findings.append(
                _finding(
                    relative,
                    "agent-profile-symlink",
                    "agent profile must be a physical regular file",
                )
            )
        elif not path.is_file():
            findings.append(
                _finding(
                    relative,
                    "agent-profile-regular-file",
                    "agent profile must be a regular file",
                )
            )
        else:
            candidates.append(path)
    return candidates, findings


def audit_agent_profiles(root: Path) -> AgentProfileAudit:
    """Discover strict recursive profiles and reject ambiguous metadata."""

    agents = root / "agents"
    if not agents.exists() and not agents.is_symlink():
        return AgentProfileAudit((), ())
    if agents.is_symlink():
        return AgentProfileAudit(
            (),
            (
                _finding(
                    "agents", "agent-profile-symlink", "agent directory is a symlink"
                ),
            ),
        )
    if not agents.is_dir():
        return AgentProfileAudit(
            (),
            (
                _finding(
                    "agents",
                    "agent-profile-directory",
                    "agent profile root must be a directory",
                ),
            ),
        )

    candidates, findings = _candidate_paths(root, agents)
    pending: list[AgentProfile] = []
    for path in candidates:
        relative = _relative(root, path)
        try:
            source = path.read_text(encoding="utf-8")
            metadata, instructions = _frontmatter(source)
        except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
            findings.append(
                _finding(
                    relative, "agent-profile-frontmatter", str(error).splitlines()[0]
                )
            )
            continue

        profile_findings: list[AgentProfileFinding] = []
        name = metadata.get("name")
        profile_name = name if isinstance(name, str) and name == path.stem else None
        if profile_name is None:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-name",
                    f"frontmatter name must equal filename {path.stem!r}",
                )
            )
        description = metadata.get("description")
        profile_description = (
            description.strip()
            if isinstance(description, str) and description.strip()
            else None
        )
        if profile_description is None:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-description",
                    "description must be a non-empty string",
                )
            )
        portable_surface = f"{profile_description or ''}\n{instructions}"
        if path.parent.name == "project-wide" and NON_PORTABLE_PROJECT_REFERENCE.search(
            portable_surface
        ):
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-non-generic",
                    "project-wide profile contains a private, provider-local, "
                    "or cross-repository contract",
                )
            )
        if "model" in metadata:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-model",
                    "provider-neutral agent profiles must not declare model",
                )
            )
        if _INLINE_PROMPT_DEFENSE in instructions:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-inline-rule",
                    f"prompt defense must be composed from {_PROMPT_DEFENSE_RULE}",
                )
            )
        try:
            tags = _tag_values(metadata)
        except (TypeError, ValueError) as error:
            profile_findings.append(
                _finding(relative, "agent-profile-tags", str(error))
            )
            tags = ()
        else:
            profile_findings.extend(_tag_findings(relative, path.parent.name, tags))
        findings.extend(profile_findings)
        if profile_findings:
            continue
        assert profile_name is not None
        assert profile_description is not None
        pending.append(
            AgentProfile(
                path=path,
                name=profile_name,
                description=profile_description,
                distribution=path.parent.name,
                tags=tags,
                rule_paths=(_PROMPT_DEFENSE_RULE,),
                instructions=instructions,
            )
        )

    by_name: dict[str, list[AgentProfile]] = {}
    for profile in pending:
        by_name.setdefault(profile.name, []).append(profile)
    ambiguous = {name for name, profiles in by_name.items() if len(profiles) > 1}
    for name in sorted(ambiguous):
        for profile in by_name[name]:
            findings.append(
                _finding(
                    _relative(root, profile.path),
                    "agent-profile-ambiguous",
                    f"profile name {name!r} exists in more than one distribution",
                )
            )

    profiles = tuple(profile for profile in pending if profile.name not in ambiguous)
    if profiles:
        rule = root / _PROMPT_DEFENSE_RULE
        if rule.is_symlink() or not rule.is_file():
            findings.append(
                _finding(
                    _PROMPT_DEFENSE_RULE,
                    "agent-profile-rule-owner",
                    "prompt-defense rule owner must be a physical regular file",
                )
            )
            profiles = ()
    return AgentProfileAudit(
        profiles, tuple(sorted(findings, key=lambda item: (item.path, item.code)))
    )
