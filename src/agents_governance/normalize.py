"""Progressive-disclosure and discovery normalization checks."""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import Catalog
from .tokens import bpe_tokens
from .validation import description_contract_error


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
    """Report oversized bodies that require an authored activation router."""

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
        destination = directory / "references" / "procedure.md"
        changes.append(
            Normalization(
                name=directory.name,
                tokens=tokens,
                lines=lines,
                destination=destination.relative_to(catalog.root).as_posix(),
            )
        )
    if apply and changes:
        names = ", ".join(change.name for change in changes)
        raise ValueError(
            "normalization requires an authored activation router and a lossless "
            f"local procedure split: {names}"
        )
    return changes
