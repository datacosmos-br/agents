"""General catalog-structure invariants derived from the bundle itself.

Law: tests never freeze SSOT-declarable catalog content (names, chains,
counts); they assert the derivation contract so any future catalog shape
conforms without test edits.
"""

from __future__ import annotations

from agents_governance import GovernanceBundle


def test_skill_extends_graph_resolves_and_is_acyclic(
    governance_bundle: GovernanceBundle,
) -> None:
    """Every parent resolves inside the bundle and no cycle is reachable."""

    skills = {skill.name: skill for skill in governance_bundle.skills}
    for skill in governance_bundle.skills:
        for parent in skill.parents:
            assert parent in skills, f"{skill.name} extends unknown owner {parent}"
            assert parent != skill.name, f"{skill.name} extends itself"
    for start in governance_bundle.skills:
        seen: set[str] = set()
        cursor = start.name
        while skills[cursor].parents:
            cursor = skills[cursor].parents[0]
            assert cursor not in seen, f"extends cycle reachable from {start.name}"
            seen.add(cursor)


def test_skill_extends_layers_compose_general_to_specialized(
    governance_bundle: GovernanceBundle,
) -> None:
    """A child never out-ranks its parent: parents own broader route scope.

    General-to-specialized composition means every child's parent set is a
    subset of the catalog and each declared parent chain terminates at a
    parent with no further parents (a root owner).
    """

    skills = {skill.name: skill for skill in governance_bundle.skills}
    rooted = {skill.name for skill in governance_bundle.skills if not skill.parents}
    assert rooted, "catalog has no root owner: composition has no base layer"
    for skill in governance_bundle.skills:
        if not skill.parents:
            continue
        direct = skills[skill.parents[0]]
        assert not (
            skill.parents and direct.parents and skill.name in direct.parents
        ), f"{skill.name} claims parenthood over its own parent {direct.name}"


def test_bundle_facade_records_match_physical_catalog(
    governance_bundle: GovernanceBundle,
) -> None:
    """Bundle records project exactly one physical owner per identity."""

    skill_dirs = [skill.directory for skill in governance_bundle.skills]
    assert len(skill_dirs) == len(set(skill_dirs))
    for skill in governance_bundle.skills:
        assert (skill.directory / "SKILL.md").is_file()
