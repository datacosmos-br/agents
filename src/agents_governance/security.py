"""Fail-closed validation for project-owned security triage documents."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

_TRACKER = re.compile(r"^(?:Bead|Ledger):\s*(?:`([^`]+)`|(manual))\s*$", re.MULTILINE | re.IGNORECASE)
_FINDING = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_DECISION = re.compile(r"^\*\*Decis(?:ão|ao)\*\*:\s*(.*)$", re.MULTILINE | re.IGNORECASE)
_EVIDENCE = re.compile(r"^\*\*(?:Evidência|Evidencia|Evidence)\*\*:\s*(.*)$", re.MULTILINE | re.IGNORECASE)
_ALLOWED_DECISIONS = ("corrigir", "corrigido", "falso-positivo")


@dataclass(frozen=True)
class SecurityFinding:
    """One blocking defect in a security triage document."""

    path: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def discover(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    """Discover scanner triage documents below explicit repository roots."""

    return tuple(sorted(
        path
        for root in roots
        for path in (root.resolve() / "docs" / "security").glob("*-triage.md")
        if path.is_file()
    ))


def _sections(text: str) -> tuple[tuple[str, str], ...]:
    matches = tuple(_FINDING.finditer(text))
    return tuple(
        (match.group(1).strip(), text[match.end(): matches[index + 1].start() if index + 1 < len(matches) else len(text)])
        for index, match in enumerate(matches)
    )


def validate_document(path: Path) -> tuple[SecurityFinding, ...]:
    """Validate traceability and closure evidence for one Markdown report."""

    text = path.read_text(encoding="utf-8")
    findings: list[SecurityFinding] = []
    if _TRACKER.search(text) is None:
        findings.append(SecurityFinding(str(path), "missing-tracker", "report must declare a canonical Bead or manual ledger"))
    sections = _sections(text)
    if not sections:
        findings.append(SecurityFinding(str(path), "missing-findings", "report must contain numbered finding sections"))
    for title, body in sections:
        decisions = _DECISION.findall(body)
        decision = decisions[-1].strip().lower() if decisions else ""
        label = f"{path}#{title}"
        if not decision:
            findings.append(SecurityFinding(label, "missing-decision", "finding decision is empty"))
            continue
        if not any(decision.startswith(value) for value in _ALLOWED_DECISIONS):
            findings.append(SecurityFinding(label, "invalid-decision", f"unsupported closing decision: {decision}"))
        evidence = _EVIDENCE.findall(body)
        if not evidence or not evidence[-1].strip():
            findings.append(SecurityFinding(label, "missing-evidence", "closed finding requires reproducible evidence"))
    return tuple(findings)


def audit(roots: tuple[Path, ...]) -> tuple[SecurityFinding, ...]:
    """Audit every discovered triage document, failing when none exist."""

    documents = discover(roots)
    if not documents:
        joined = ", ".join(str(root.resolve()) for root in roots)
        return (SecurityFinding(joined, "missing-report", "no docs/security/*-triage.md documents found"),)
    return tuple(finding for path in documents for finding in validate_document(path))
