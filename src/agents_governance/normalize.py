"""Lossless progressive-disclosure normalization for oversized skills."""

from __future__ import annotations

import re
from dataclasses import dataclass

import yaml

from .catalog import Catalog
from .tokens import bpe_tokens

_LOCAL_LINK = re.compile(r"(!?\[[^\]]+\]\()([^)]+)(\))")
_KEYWORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9+.#/_-]*")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "code",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "use",
    "uses",
    "using",
    "when",
    "with",
    "without",
    "workflow",
    "skill",
    "skills",
    "project",
    "projects",
}


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


def keyword_description(name: str, description: str, *, limit: int = 10) -> str:
    """Reduce prose to stable, discriminating trigger keywords."""

    candidates = [*name.split("-"), *_KEYWORD.findall(description)]
    keywords: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        keyword = candidate.strip("._-/").lower()
        if len(keyword) < 2 or keyword in _STOPWORDS or keyword in seen:
            continue
        seen.add(keyword)
        keywords.append(keyword)
        if len(keywords) == limit:
            break
    return ", ".join(keywords)


def normalize_descriptions(catalog: Catalog, *, apply: bool) -> list[Normalization]:
    """Replace every skill discovery description with compact keyword lists."""

    changes: list[Normalization] = []
    for directory in catalog.skill_dirs():
        if catalog.policy(directory.name).updates == "forbidden":
            continue
        skill = directory / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        marker = text.find("\n---\n", 4)
        if not text.startswith("---\n") or marker < 0:
            continue
        metadata = yaml.safe_load(text[4:marker])
        if not isinstance(metadata, dict) or not isinstance(
            metadata.get("description"), str
        ):
            continue
        description = keyword_description(directory.name, metadata["description"])
        if metadata["description"] != description:
            changes.append(
                Normalization(
                    name=directory.name,
                    tokens=len(_KEYWORD.findall(metadata["description"])),
                    lines=1,
                    destination=(skill.relative_to(catalog.root)).as_posix(),
                )
            )
            if apply:
                metadata["description"] = description
                frontmatter = yaml.safe_dump(
                    metadata, sort_keys=False, allow_unicode=True, width=4096
                ).rstrip()
                skill.write_text(
                    f"---\n{frontmatter}\n---\n{text[marker + 5 :]}", encoding="utf-8"
                )
        openai = directory / "agents" / "openai.yaml"
        if not openai.is_file():
            continue
        openai_metadata = yaml.safe_load(openai.read_text(encoding="utf-8"))
        if not isinstance(openai_metadata, dict) or not isinstance(
            openai_metadata.get("description"), str
        ):
            continue
        openai_description = keyword_description(
            directory.name, openai_metadata["description"]
        )
        if openai_metadata["description"] == openai_description:
            continue
        changes.append(
            Normalization(
                name=directory.name,
                tokens=len(_KEYWORD.findall(openai_metadata["description"])),
                lines=1,
                destination=openai.relative_to(catalog.root).as_posix(),
            )
        )
        if apply:
            openai_metadata["description"] = openai_description
            openai.write_text(
                yaml.safe_dump(
                    openai_metadata, sort_keys=False, allow_unicode=True, width=4096
                ),
                encoding="utf-8",
            )
    return changes


def normalize(catalog: Catalog, *, apply: bool) -> list[Normalization]:
    """Move oversized bodies into one required procedure reference."""

    changes: list[Normalization] = []
    for directory in catalog.skill_dirs():
        skill = directory / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        policy = catalog.policy(directory.name)
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
        destination.write_text(_rebase_links(body), encoding="utf-8")
        title = directory.name.replace("-", " ").title()
        router = (
            f"{frontmatter}\n# {title}\n\n"
            "This file is the activation router. Before acting, read "
            "[the complete procedure](references/procedure.md) in full and follow it. "
            "The referenced procedure is canonical for this skill; do not improvise "
            "missing steps or restore an upstream synchronization path.\n"
        )
        skill.write_text(router, encoding="utf-8")
    return changes
