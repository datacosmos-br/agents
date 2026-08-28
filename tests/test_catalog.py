from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agents_governance.catalog import Catalog, SkillCategory

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

_BUDGETS = {
    "router_tokens": 500,
    "frozen_tokens": 1200,
    "on_demand_tokens": 5000,
    "max_lines": 500,
}
_BASE_TAGS = (
    "policy:strict-execution",
    "provenance:agents-owned",
    "updates:manual",
    "usage:on-demand",
)


def _write_config(root: Path, **legacy: object) -> None:
    (root / "config").mkdir(exist_ok=True)
    payload: dict[str, object] = {"version": 2, "budgets": _BUDGETS}
    payload.update(legacy)
    (root / "config" / "skills.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_skill(
    root: Path,
    category: str,
    name: str,
    *,
    declared_name: str | None = None,
    tags: tuple[str, ...] = _BASE_TAGS,
) -> Path:
    directory = root / "skills" / category / name
    directory.mkdir(parents=True)
    encoded_tags = json.dumps(tags, separators=(",", ":"))
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {declared_name or name}\n"
        f"description: {name}, validation\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
        f"  aihub.tags: '{encoded_tags}'\n"
        "---\n"
        f"# {name}\n",
        encoding="utf-8",
    )
    return directory


def test_inventory_is_recursive_deterministic_and_typed(tmp_path: Path) -> None:
    _write_config(tmp_path)
    directory = _write_skill(tmp_path, "agent-wide", "example")

    catalog = Catalog(tmp_path)
    first = catalog.inventory()
    second = catalog.inventory()

    assert first == second
    assert catalog.skill_dirs() == (directory,)
    assert first == [
        {
            "name": "example",
            "owner": "agents",
            "category": "agent-wide",
            "class": "on_demand",
            "provenance": "agents-owned",
            "updates": "manual",
            "max_tokens": 5000,
            "max_lines": 500,
            "distributions": ["personal"],
            "tags": list(_BASE_TAGS),
            "path": "skills/agent-wide/example",
            "digest": Catalog.digest_tree(directory),
        }
    ]


def test_legacy_distribution_registries_are_rejected(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        personal=["project-capability"],
        project_generic=["agent-capability"],
        technologies={"wrong": {"skills": ["agent-capability"]}},
    )
    _write_skill(tmp_path, "agent-wide", "agent-capability")
    _write_skill(tmp_path, "project-wide", "project-capability")

    with pytest.raises(ValueError, match="fields must equal budgets, version"):
        Catalog(tmp_path)


@pytest.mark.parametrize(
    "legacy_field",
    ["author", "bundle", "scope", "triggers", "version"],
)
def test_legacy_skill_frontmatter_fields_are_rejected(
    tmp_path: Path, legacy_field: str
) -> None:
    _write_config(tmp_path)
    directory = _write_skill(tmp_path, "agent-wide", "example")
    skill = directory / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    skill.write_text(
        text.replace("metadata:\n", f"{legacy_field}: legacy\nmetadata:\n"),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError, match=f"unsupported skill frontmatter fields: {legacy_field}"
    ):
        Catalog(tmp_path)


def test_inventory_lock_has_one_exact_check_and_render_contract(
    tmp_path: Path,
) -> None:
    _write_config(tmp_path)
    _write_skill(tmp_path, "agent-wide", "example")
    catalog = Catalog(tmp_path)
    lock = tmp_path / "skills.lock.json"

    with pytest.raises(FileNotFoundError, match="inventory lock is missing"):
        catalog.require_inventory_lock()

    lock.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        catalog.require_inventory_lock()

    lock.write_text('{"skills": [], "version": 1}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="differs from discovery"):
        catalog.require_inventory_lock()

    lock.write_text(catalog.render_inventory(), encoding="utf-8")
    catalog.require_inventory_lock()


def test_repository_catalog_matches_current_78_skill_acceptance_contract() -> None:
    catalog = Catalog(REPOSITORY_ROOT)
    names = {record.name for record in catalog.records()}

    assert len(names) == 78
    assert {"fix-forward-collaboration", "plan-focus-recovery"} <= names


def test_conditional_profiles_are_derived_from_local_tags(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write_skill(
        tmp_path,
        "technology",
        "go-development",
        tags=(
            "activation:detected",
            "detect:marker:go.mod",
            "detect:marker:go.work",
            "provenance:agents-owned",
            "route:project",
            "technology:go",
            "updates:manual",
            "usage:router",
        ),
    )
    _write_skill(
        tmp_path,
        "framework",
        "react-frontend",
        tags=(
            "activation:detected",
            "detect:dependency:npm:react",
            "framework:react",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )

    catalog = Catalog(tmp_path)

    assert catalog.names_for("project-capability:technology:go") == {"go-development"}
    assert catalog.names_for("project-capability:framework:react") == {"react-frontend"}


@pytest.mark.parametrize(
    ("tags", "message"),
    [
        ((_BASE_TAGS[0], _BASE_TAGS[0], *_BASE_TAGS[1:]), "tags must be unique"),
        (tuple(reversed(_BASE_TAGS)), "tags must be sorted"),
        ((_BASE_TAGS[0], _BASE_TAGS[2]), "exactly one usage"),
        ((_BASE_TAGS[0], "updates:manual", "usage:unknown"), "unsupported tag"),
        (("custom:value", *_BASE_TAGS), "unsupported tag namespace"),
        (
            (
                "policy:compatibility",
                "provenance:agents-owned",
                "updates:manual",
                "usage:on-demand",
            ),
            "unsupported tag",
        ),
    ],
)
def test_tag_contract_fails_closed(
    tmp_path: Path, tags: tuple[str, ...], message: str
) -> None:
    _write_config(tmp_path)
    _write_skill(tmp_path, "agent-wide", "example", tags=tags)

    with pytest.raises(ValueError, match=message):
        Catalog(tmp_path)


@pytest.mark.parametrize(
    ("raw_tags", "exception"),
    [
        ('["unterminated"', json.JSONDecodeError),
        ('{"usage":"on-demand"}', TypeError),
    ],
)
def test_tags_must_be_a_json_array_string(
    tmp_path: Path, raw_tags: str, exception: type[Exception]
) -> None:
    _write_config(tmp_path)
    skill = _write_skill(tmp_path, "agent-wide", "example")
    skill_file = skill / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    start = text.index("  aihub.tags:")
    end = text.index("\n", start)
    skill_file.write_text(
        f"{text[:start]}  aihub.tags: '{raw_tags}'{text[end:]}", encoding="utf-8"
    )

    with pytest.raises(exception):
        Catalog(tmp_path)


@pytest.mark.parametrize(
    ("tags", "message"),
    [
        (
            (
                "provenance:agents-owned",
                "route:project",
                "technology:go",
                "updates:manual",
                "usage:router",
            ),
            "exactly one activation",
        ),
        (
            (
                "activation:detected",
                "provenance:agents-owned",
                "route:project",
                "technology:go",
                "updates:manual",
                "usage:router",
            ),
            "requires runtime detector",
        ),
        (
            (
                "activation:detected",
                "detect:marker:go.mod",
                "provenance:agents-owned",
                "route:project",
                "updates:manual",
                "usage:router",
            ),
            "category tag is required",
        ),
    ],
)
def test_conditional_category_contract_fails_closed(
    tmp_path: Path, tags: tuple[str, ...], message: str
) -> None:
    _write_config(tmp_path)
    _write_skill(tmp_path, "technology", "go-development", tags=tags)

    with pytest.raises(ValueError, match=message):
        Catalog(tmp_path)


def test_duplicate_names_across_categories_are_rejected(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _write_skill(tmp_path, "agent-wide", "example")
    _write_skill(tmp_path, "project-wide", "example")

    with pytest.raises(ValueError, match="duplicate skill name: example"):
        Catalog(tmp_path)


def test_noncanonical_skill_path_is_rejected(tmp_path: Path) -> None:
    _write_config(tmp_path)
    flat = tmp_path / "skills" / "example"
    flat.mkdir(parents=True)
    (flat / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, validation\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="skill path must be"):
        Catalog(tmp_path)


def test_forbidden_skill_preserves_frozen_budget_and_is_not_distributed(
    tmp_path: Path,
) -> None:
    _write_config(tmp_path)
    _write_skill(
        tmp_path,
        "agent-wide",
        "vendor-frozen",
        tags=(
            "provenance:vendor",
            "updates:forbidden",
            "usage:frozen",
        ),
    )

    catalog = Catalog(tmp_path)
    policy = catalog.policy("vendor-frozen")

    assert policy.max_tokens == 1200
    assert policy.updates == "forbidden"
    assert policy.distributions == ()
    assert catalog.names_for("personal") == set()


def test_content_digest_stays_stable_while_physical_contract_tracks_mode_and_type(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.write_text("same payload\n", encoding="utf-8")
    source.chmod(0o600)
    private_content = Catalog.digest_tree(source)
    private_physical = Catalog.physical_tree_contract(source)

    source.chmod(0o644)
    public_content = Catalog.digest_tree(source)
    public_physical = Catalog.physical_tree_contract(source)

    source.unlink()
    source.mkdir()
    directory_physical = Catalog.physical_tree_contract(source)

    assert private_content == public_content
    assert private_physical != public_physical
    assert public_physical != directory_physical


def test_digest_rejects_symlinks_and_special_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    regular = source / "regular.txt"
    regular.write_text("payload\n", encoding="utf-8")
    symlink = source / "linked.txt"
    symlink.symlink_to(regular)

    with pytest.raises(ValueError, match="symlink"):
        Catalog.digest_tree(source)

    symlink.unlink()
    fifo = source / "events.fifo"
    os.mkfifo(fifo)

    with pytest.raises(ValueError, match="unsupported file type"):
        Catalog.digest_tree(source)


def test_canonical_catalog_is_exhaustive_disjoint_and_agents_owned() -> None:
    catalog = Catalog(REPOSITORY_ROOT)
    inventory = catalog.inventory()

    assert {item["category"] for item in inventory} <= {
        category.value for category in SkillCategory
    }
    assert {item["provenance"] for item in inventory} == {"agents-owned"}
    assert {item["name"] for item in inventory} == {
        directory.name for directory in catalog.skill_dirs()
    }
    catalog.require_inventory_lock()


def test_canonical_skills_have_no_import_registry_identity() -> None:
    skills = REPOSITORY_ROOT / "skills"
    legacy_prefixes = (
        "aiskillstore-",
        "benchflow-",
        "copyleftdev-",
        "diegosouzapw-",
        "jamie-bitflight-",
        "majiayu000-",
    )

    assert not any(
        directory.name.startswith(legacy_prefixes)
        for directory in skills.glob("*/*")
        if directory.is_dir()
    )
    assert list(skills.rglob("metadata.json")) == []
    assert list(skills.rglob("skill-report.json")) == []
    for path in skills.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            assert "skillshare" not in text, path
            assert "skillsmp synced skills" not in text, path
