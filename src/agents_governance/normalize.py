"""Lossless progressive-disclosure normalization for oversized skills."""

from __future__ import annotations

import re
import stat
from dataclasses import dataclass
from pathlib import Path

from .atomic_io import discard_physical_file, stage_text
from .catalog import Catalog
from .tokens import bpe_tokens
from .validation import description_contract_error

_LOCAL_LINK = re.compile(r"(!?\[[^\]]+\]\()([^)]+)(\))")


def _rebase_links(body: str) -> str:
    """Keep skill-root-relative Markdown links valid after moving one level down."""

    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#", "/", "../")):
            return match.group(0)
        return f"{match.group(1)}../{target}{match.group(3)}"

    return _LOCAL_LINK.sub(replace, body)


@dataclass(frozen=True)
class Normalization:
    """One skill requiring or receiving normalization."""

    name: str
    tokens: int
    lines: int
    destination: str


def normalize_descriptions(catalog: Catalog, *, apply: bool) -> list[Normalization]:
    """Report descriptions that require a semantic author rewrite."""

    catalog.require_valid()
    changes: list[Normalization] = []
    for directory in catalog.skill_dirs():
        if catalog.policy_for(directory).updates == "forbidden":
            continue
        skill = directory / "SKILL.md"
        frontmatter = Catalog._frontmatter(skill)
        description = frontmatter.get("description")
        if description_contract_error(description) is not None:
            changes.append(
                Normalization(
                    name=directory.name,
                    tokens=len(description.split())
                    if isinstance(description, str)
                    else 0,
                    lines=1,
                    destination=(skill.relative_to(catalog.root)).as_posix(),
                )
            )
    if apply and changes:
        names = ", ".join(change.name for change in changes)
        raise ValueError(
            "description normalization requires an authored discriminating keyword "
            f"list: {names}"
        )
    return changes


def normalize(catalog: Catalog, *, apply: bool) -> list[Normalization]:
    """Move oversized bodies into one required procedure reference."""

    catalog.require_valid()
    changes: list[Normalization] = []
    for directory in catalog.skill_dirs():
        skill = directory / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        policy = catalog.policy_for(directory)
        if policy.updates == "forbidden":
            continue
        tokens = bpe_tokens(skill, catalog.root)
        lines = len(text.splitlines())
        if tokens <= policy.max_tokens and lines <= policy.max_lines:
            continue
        marker = text.find("\n---\n", 4)
        if not text.startswith("---\n") or marker < 0:
            continue
        destination = directory / "references" / "procedure.md"
        changes.append(
            Normalization(
                name=directory.name,
                tokens=tokens,
                lines=lines,
                destination=destination.relative_to(catalog.root).as_posix(),
            )
        )
        if not apply:
            continue
        if destination.exists():
            raise FileExistsError(
                f"refusing to replace existing procedure: {destination}"
            )
        frontmatter = text[: marker + 5]
        body = text[marker + 5 :].lstrip()
        destination.parent.mkdir(parents=True, exist_ok=True)
        title = directory.name.replace("-", " ").title()
        router = (
            f"{frontmatter}\n# {title}\n\n"
            "This file is the activation router. Before acting, read "
            "[the complete procedure](references/procedure.md) in full and follow it. "
            "The referenced procedure is canonical for this skill; do not improvise "
            "missing steps or restore an upstream synchronization path.\n"
        )
        procedure_candidate = stage_text(
            destination,
            _rebase_links(body),
            mode=stat.S_IMODE(skill.stat().st_mode),
        )
        try:
            router_candidate = stage_text(skill, router)
        except BaseException as error:
            _rollback_files((procedure_candidate,), error)
            raise
        procedure_installed = False
        try:
            procedure_candidate.replace(destination)
            procedure_installed = True
            router_candidate.replace(skill)
        except BaseException as error:
            rollback = [procedure_candidate, router_candidate]
            if procedure_installed:
                rollback.append(destination)
            _rollback_files(tuple(rollback), error)
            raise
    return changes


def _rollback_files(paths: tuple[Path, ...], error: BaseException) -> None:
    cleanup_errors: list[Exception] = []
    for path in paths:
        try:
            discard_physical_file(path)
        except (OSError, RuntimeError) as cleanup_error:
            cleanup_errors.append(cleanup_error)
    if cleanup_errors:
        error.add_note(
            "normalization rollback failed: "
            + "; ".join(str(item) for item in cleanup_errors)
        )
        raise error from cleanup_errors[0]
