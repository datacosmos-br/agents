from __future__ import annotations

from pathlib import Path

from agents_governance.security import audit, validate_document


def _report(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "docs" / "security" / "semgrep-triage.md"
    path.parent.mkdir(parents=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_complete_finding_is_accepted(tmp_path: Path) -> None:
    path = _report(tmp_path, "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · MEDIUM · `rule`\n\n**Decisão**: corrigido\n\n**Evidência**: `semgrep scan` retornou código 0 sem o achado.\n")
    assert validate_document(path) == ()


def test_empty_decision_fails_closed(tmp_path: Path) -> None:
    path = _report(tmp_path, "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**:\n")
    assert [item.code for item in validate_document(path)] == ["missing-decision"]


def test_risk_acceptance_is_not_a_closing_decision(tmp_path: Path) -> None:
    path = _report(tmp_path, "# Triagem\n\nBead: `project-123`\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**: risco-aceito\n\n**Evidência**: nenhuma\n")
    assert [item.code for item in validate_document(path)] == ["invalid-decision"]


def test_missing_report_is_blocking(tmp_path: Path) -> None:
    assert audit((tmp_path,))[0].code == "missing-report"


def test_manual_ledger_is_an_explicit_tracker(tmp_path: Path) -> None:
    path = _report(tmp_path, "# Triagem\n\nLedger: manual\n\n## Findings\n\n### 1 · LOW · `rule`\n\n**Decisão**: corrigido\n\n**Evidência**: scanner retornou código 0.\n")
    assert validate_document(path) == ()
