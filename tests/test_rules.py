from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from agents_governance.rules import RuleActivation, audit_rule_specs


def _write_rule(root: Path, relative: str, contents: str) -> Path:
    path = root / "rules" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    return path


def _codes(root: Path) -> set[str]:
    return {finding.code for finding in audit_rule_specs(root).findings}


def test_recursive_discovery_derives_identity_and_activation_without_registry(
    tmp_path: Path,
) -> None:
    baseline = _write_rule(
        tmp_path,
        "baseline.md",
        "# Baseline\n\nThis rule is always active.\n",
    )
    scoped = _write_rule(
        tmp_path,
        "python/typing.md",
        "---\n"
        "description: Apply strict Python typing in matching project files.\n"
        "globs: ['*.py', '**/*.py', 'pyproject.toml']\n"
        "---\n\n"
        "# Python typing\n\n"
        "Compose the [baseline](../baseline.md#baseline).\n"
        "Canonical web sources such as [Python](https://www.python.org/) are external.\n",
    )
    _write_rule(
        tmp_path,
        "security/prompt-defense.md",
        "---\n"
        "description: Compose prompt-defense constraints into every agent.\n"
        "---\n\n"
        "# Prompt defense\n",
    )

    audit = audit_rule_specs(tmp_path)

    assert audit.findings == ()
    assert [rule.identity for rule in audit.rules] == [
        "baseline",
        "python/typing",
        "security/prompt-defense",
    ]
    always, typed, described = audit.rules
    assert always.path == baseline
    assert always.description is None
    assert always.activation is RuleActivation.ALWAYS
    assert always.globs == ()
    assert typed.path == scoped
    assert typed.activation is RuleActivation.PATH_SCOPED
    assert typed.globs == ("*.py", "**/*.py", "pyproject.toml")
    assert typed.references == ("rules/baseline.md",)
    assert described.activation is RuleActivation.ALWAYS


@pytest.mark.parametrize(
    ("contents", "code"),
    [
        ("---\ndescription: [broken\n---\n# Rule\n", "rule-frontmatter"),
        ("---\n---\n# Rule\n", "rule-frontmatter"),
        ("---\nname: invented\n---\n# Rule\n", "rule-field"),
        ("---\ndescription: ''\n---\n# Rule\n", "rule-description"),
        ("---\nglobs: 7\n---\n# Rule\n", "rule-globs"),
        ("---\nglobs: []\n---\n# Rule\n", "rule-globs"),
        ("---\nglobs: ../outside.py\n---\n# Rule\n", "rule-globs"),
        (
            "---\nglobs: ['*.py', '*.py']\n---\n# Rule\n",
            "rule-duplicate",
        ),
        (
            "---\ndescription: First.\ndescription: Second.\n---\n# Rule\n",
            "rule-frontmatter",
        ),
        ("---\ndescription: Valid.\n---\n   \n", "rule-body"),
    ],
)
def test_frontmatter_and_body_fail_closed(
    tmp_path: Path, contents: str, code: str
) -> None:
    _write_rule(tmp_path, "invalid.md", contents)

    audit = audit_rule_specs(tmp_path)

    assert code in {finding.code for finding in audit.findings}
    assert audit.rules == ()


def test_discovery_rejects_invalid_paths_symlinks_and_casefold_duplicates(
    tmp_path: Path,
) -> None:
    _write_rule(tmp_path, "valid.md", "# Valid\n")
    _write_rule(tmp_path, "Upper.md", "# Upper\n")
    _write_rule(tmp_path, "upper.md", "# Lower\n")
    _write_rule(tmp_path, "Bad-Directory/nested.md", "# Nested\n")
    (tmp_path / "rules" / "foreign.json").write_text("{}\n", encoding="utf-8")
    linked_source = tmp_path / "linked-source.md"
    linked_source.write_text("# Linked\n", encoding="utf-8")
    (tmp_path / "rules" / "linked.md").symlink_to(linked_source)
    linked_directory = tmp_path / "linked-directory"
    linked_directory.mkdir()
    (tmp_path / "rules" / "linked-dir").symlink_to(
        linked_directory, target_is_directory=True
    )

    audit = audit_rule_specs(tmp_path)
    findings = {(finding.path, finding.code) for finding in audit.findings}

    assert ("rules/foreign.json", "rule-path") in findings
    assert ("rules/Bad-Directory", "rule-path") in findings
    assert ("rules/linked.md", "rule-symlink") in findings
    assert ("rules/linked-dir", "rule-symlink") in findings
    assert ("rules/Upper.md", "rule-path") in findings
    assert ("rules/Upper.md", "rule-duplicate") in findings
    assert ("rules/upper.md", "rule-duplicate") in findings
    assert [rule.identity for rule in audit.rules] == ["valid"]


@pytest.mark.parametrize(
    "target",
    [
        "missing.md",
        "../../outside.md",
        "/absolute.md",
        "file:///outside.md",
        "asset.txt",
    ],
)
def test_invalid_local_references_are_blocking(tmp_path: Path, target: str) -> None:
    _write_rule(
        tmp_path,
        "workflow/source.md",
        f"# Source\n\nRead [the target]({target}).\n",
    )

    audit = audit_rule_specs(tmp_path)

    assert _codes(tmp_path) == {"rule-reference"}
    assert audit.rules == ()


def test_reference_through_symlink_is_rejected(tmp_path: Path) -> None:
    target = _write_rule(tmp_path, "target.md", "# Target\n")
    (tmp_path / "rules" / "alias.md").symlink_to(target)
    _write_rule(
        tmp_path,
        "source.md",
        "# Source\n\nRead [the target](alias.md).\n",
    )

    audit = audit_rule_specs(tmp_path)

    assert ("rules/alias.md", "rule-symlink") in {
        (finding.path, finding.code) for finding in audit.findings
    }
    assert ("rules/source.md", "rule-reference") in {
        (finding.path, finding.code) for finding in audit.findings
    }
    assert [rule.identity for rule in audit.rules] == ["target"]


def test_missing_non_directory_and_symlinked_rule_roots_fail_loudly(
    tmp_path: Path,
) -> None:
    assert _codes(tmp_path) == {"rule-root"}

    rules = tmp_path / "rules"
    rules.write_text("not a directory\n", encoding="utf-8")
    assert _codes(tmp_path) == {"rule-root"}

    rules.unlink()
    target = tmp_path / "rule-source"
    target.mkdir()
    rules.symlink_to(target, target_is_directory=True)
    assert _codes(tmp_path) == {"rule-symlink"}


def test_rule_spec_rejects_activation_not_derived_from_path_scopes(
    tmp_path: Path,
) -> None:
    _write_rule(tmp_path, "baseline.md", "# Baseline\n")
    audit = audit_rule_specs(tmp_path)
    assert audit.findings == ()

    with pytest.raises(ValueError, match="activation"):
        replace(audit.rules[0], activation=RuleActivation.PATH_SCOPED)

    with pytest.raises(ValueError, match="path-derived"):
        replace(audit.rules[0], identity="different")


def test_duplicate_rule_bodies_are_competing_owners(tmp_path: Path) -> None:
    _write_rule(tmp_path, "first.md", "# One authority\n")
    _write_rule(tmp_path, "nested/second.md", "# One authority\n")

    audit = audit_rule_specs(tmp_path)

    assert audit.rules == ()
    assert [(finding.path, finding.code) for finding in audit.findings] == [
        ("rules/first.md", "rule-duplicate"),
        ("rules/nested/second.md", "rule-duplicate"),
    ]
