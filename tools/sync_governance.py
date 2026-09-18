"""Project the governance capsule into every provider surface.

This tool is the single writable authority for generated hook scripts, the
OpenCode governance plugin, and instruction-pointer files (CLAUDE.md,
GEMINI.md). It composes the capsule from the validated ``GovernanceBundle``
and embeds it deterministically into each provider's delivery mechanism.

Run via ``make gen``. The rendering, fixed-point validation, and manifest
maintenance live in the dev-only ``governance_projection`` tool module
(ADR-0008: the package ships no projector); this driver only loads the
bundle and invokes the owner. The tool validates fixed-point idempotence
by generating twice and comparing a content-addressed snapshot.
"""

from __future__ import annotations

from pathlib import Path

from governance_projection import project_from_bundle

from agents_governance import GovernanceBundle


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    bundle = GovernanceBundle.load(root)
    project_from_bundle(root, bundle)


if __name__ == "__main__":
    main()
