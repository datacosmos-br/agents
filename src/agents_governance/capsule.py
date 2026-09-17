"""Compose the session governance capsule from canonical sources.

The capsule is a compact, content-addressed rendering of the always-on
governance contract: the law prelude boundary, every bootstrap rule's
standing summary with its approval tags, and the capability index for
bootstrap skills and all declared commands.

Provider hook scripts, instruction pointers, and runtime plugins never
embed a hand-maintained capsule — they consume this projection. The
SHA-256 digest in the capsule header is the hash of the body, letting
every consumer prove freshness in O(1).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .approvals import approval_tags
from .bundle import GovernanceBundle

CAPSULE_MARKER = "AIHUB-GOVERNANCE-CAPSULE v1"
OPCODE_MARKER = "AIHUB-GOVERNANCE"

_CAPSULE_INTRO = (
    "This projection is derived from `GovernanceBundle`; edit canonical "
    "`AGENTS.md`, `rules/`, `skills/`, or `commands/`, never this output. "
    "AI Hub owns publication and provider activation. The operator's newest "
    "request has precedence. Provider hooks are delivery mechanisms, not policy "
    "owners. Each rule below is the standing summary of its canonical file in "
    "`rules/`; open that file when a decision turns on its detail."
)


@dataclass(frozen=True)
class Capsule:
    """A content-addressed session governance capsule.

    *text* is the full on-disk/on-wire string: header comment line, the
    body, and a trailing newline. *body* is everything after the header
    line, rstripped of trailing whitespace — its SHA-256 is the digest
    embedded in the header. *opencode_digest* hashes the full text and
    is used by the OpenCode block marker.
    """

    text: str
    body: str
    digest: str

    @property
    def header(self) -> str:
        return f"<!-- {CAPSULE_MARKER} sha256:{self.digest} -->"

    @property
    def opencode_digest(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def render_capsule(bundle: GovernanceBundle) -> Capsule:
    """Render the session capsule from the validated governance bundle."""

    by_identity = {rule.identity: rule for rule in bundle.rules}
    lines: list[str] = [
        "# Generated session governance capsule",
        "",
        _CAPSULE_INTRO,
    ]
    for ident in bundle.config.bootstrap_rules:
        rule = by_identity[ident]
        lines.extend(
            [
                "",
                f"## Rule `{rule.identity}`",
                "",
                rule.capsule_summary.strip(),
                "",
            ]
        )
        approves = approval_tags(rule.tags)
        if approves:
            lines.append(f"<!-- aihub.approval: {'; '.join(approves)} -->")
    lines.extend(
        [
            "",
            "## Capability indexes",
            "",
            f"Skills: {', '.join(bundle.config.bootstrap_skills)}",
            f"Commands: {', '.join(cmd.name for cmd in bundle.commands)}",
        ]
    )
    body = "\n".join(lines)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    text = f"<!-- {CAPSULE_MARKER} sha256:{digest} -->\n{body}\n"
    return Capsule(text, body, digest)


__all__ = ("CAPSULE_MARKER", "OPCODE_MARKER", "Capsule", "render_capsule")
