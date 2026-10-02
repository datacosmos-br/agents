"""Observable behavior of the supersedes history proof across Git locales.

``audit_precedence`` asks Git whether the audited root is the authored
repository. Absence of a repository is a legal state (the packaged snapshot
carries no history), so the answer must not depend on the language Git
speaks. Each scenario runs the public function in a child interpreter whose
environment selects a non-English message locale, against real directories
and a real Git repository.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_NON_ENGLISH = {"LANG": "pt_BR.UTF-8", "LANGUAGE": "pt_BR:pt"}

_AUDIT = """
import sys
from pathlib import Path
from agents_governance.approvals import ApprovedArtifact, audit_precedence

root = Path(sys.argv[1])
artifact = ApprovedArtifact(
    identity="rule:successor",
    tags=(f"supersedes:{sys.argv[2]}",),
    source=root / "rules" / "successor.md",
)
audit_precedence(root, (artifact,))
"""


def _audit(root: Path, superseded: str) -> subprocess.CompletedProcess[str]:
    environment = {
        name: value for name, value in os.environ.items() if not name.startswith("LC_")
    }
    environment.update(_NON_ENGLISH)
    environment["GIT_CEILING_DIRECTORIES"] = str(root.parent)
    return subprocess.run(
        (sys.executable, "-c", _AUDIT, str(root), superseded),
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(
        (
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=approvals-test",
            "-c",
            "user.email=approvals-test@example.invalid",
            *arguments,
        ),
        check=True,
        capture_output=True,
    )


def test_non_repository_root_takes_the_inventory_proof_under_non_english_locale(
    tmp_path: Path,
) -> None:
    snapshot = tmp_path / "packaged"
    snapshot.mkdir()

    result = _audit(snapshot, "rule:predecessor")

    assert result.returncode == 0, result.stderr


def test_repository_root_requires_history_under_non_english_locale(
    tmp_path: Path,
) -> None:
    root = tmp_path / "authored"
    root.mkdir()
    _git(root, "init", "--quiet")
    (root / "rules").mkdir()
    (root / "rules" / "predecessor.md").write_text("# predecessor\n")
    _git(root, "add", "rules/predecessor.md")
    _git(root, "commit", "--quiet", "-m", "predecessor")
    _git(root, "rm", "--quiet", "rules/predecessor.md")
    _git(root, "commit", "--quiet", "-m", "retire predecessor")

    retired = _audit(root, "rule:predecessor")
    unknown = _audit(root, "rule:never-authored")

    assert retired.returncode == 0, retired.stderr
    assert unknown.returncode == 1
    assert "does not resolve through Git history" in unknown.stderr
