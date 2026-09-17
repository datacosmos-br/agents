"""Exercise the Beads reconciliation script through its public skill resource."""

from __future__ import annotations

import csv
import io
import json
import os
import shlex
import subprocess
from pathlib import Path

from agents_governance import GovernanceBundle


def _issue(identifier: str, *, status: str = "open") -> dict[str, object]:
    return {
        "id": identifier,
        "revision": 1,
        "status": status,
        "priority": 2,
        "issue_type": "task",
        "title": f"Reconcile {identifier}",
        "parent": None,
        "assignee": None,
        "defer_until": None,
        "labels": [],
        "description": "A complete public behavior fixture for reconciliation output.",
    }


def _run(
    governance_bundle: GovernanceBundle,
    tmp_path: Path,
    inventory: object,
    *selection: str,
) -> subprocess.CompletedProcess[str]:
    skill = next(
        item for item in governance_bundle.skills if item.name == "beads-organization"
    )
    script = skill.directory / "scripts" / "reconcile-inventory.sh"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    bd = fake_bin / "bd"
    payload = shlex.quote(json.dumps(inventory))
    bd.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        '[[ "$*" == "list --all --limit 0 --flat --json" ]]\n'
        f"printf '%s\\n' {payload}\n",
        encoding="utf-8",
    )
    bd.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    repository = Path(__file__).resolve().parents[1]
    return subprocess.run(
        (
            str(script),
            "--limit",
            "0",
            "--integration",
            "HEAD",
            "--dry-run",
            *selection,
        ),
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def _rows(result: subprocess.CompletedProcess[str]) -> list[dict[str, str]]:
    assert result.returncode == 0, result.stderr
    return list(csv.DictReader(io.StringIO(result.stdout)))


def test_selected_existing_bead_is_the_only_csv_row(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    result = _run(
        governance_bundle,
        tmp_path,
        [_issue("ag-1"), _issue("ag-2")],
        "--beads",
        "ag-2",
    )

    assert [row["id"] for row in _rows(result)] == ["ag-2"]


def test_repeated_and_comma_separated_ids_are_selected_once(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    result = _run(
        governance_bundle,
        tmp_path,
        [_issue("ag-1"), _issue("ag-2"), _issue("ag-3")],
        "--beads",
        "ag-2,ag-1",
        "--beads",
        "ag-2",
    )

    assert [row["id"] for row in _rows(result)] == ["ag-1", "ag-2"]


def test_unknown_selected_id_fails_without_csv(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    result = _run(
        governance_bundle,
        tmp_path,
        [_issue("ag-1")],
        "--beads",
        "ag-missing",
    )

    assert result.returncode != 0
    assert not result.stdout
    assert "unknown bead IDs: ag-missing" in result.stderr


def test_empty_selection_includes_every_non_closed_bead(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    result = _run(
        governance_bundle,
        tmp_path,
        [_issue("ag-1"), _issue("ag-2"), _issue("ag-closed", status="closed")],
    )

    assert [row["id"] for row in _rows(result)] == ["ag-1", "ag-2"]


def test_object_shaped_bd_list_payload_is_rejected(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    result = _run(
        governance_bundle,
        tmp_path,
        {"issues": [_issue("ag-1")]},
    )

    assert result.returncode != 0
    assert not result.stdout
    assert "bd list JSON must be an array" in result.stderr


def test_requested_id_lookup_does_not_index_the_requested_array_as_an_object(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    result = _run(
        governance_bundle,
        tmp_path,
        [_issue("ag-regression")],
        "--beads",
        "ag-regression",
    )

    assert [row["id"] for row in _rows(result)] == ["ag-regression"]
    assert 'Cannot index array with string "id"' not in result.stderr
