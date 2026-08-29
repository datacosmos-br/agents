"""Locate canonical data files bundled with the installed runtime.

For a release wheel, all canonical data (config/, skills/, rules/, etc.) is
bundled under ``_data`` inside the package.  For an editable / development
install the data files remain at the source checkout root and are resolved via
PEP 610 metadata (see :mod:`provenance`).
"""

from __future__ import annotations

from pathlib import Path


def resource_root() -> Path:
    """Return the filesystem path to canonical data files.

    A release wheel bundles data under ``_data/`` inside the package directory;
    that path is returned directly.  An editable / development install has no
    ``_data`` directory, so the source checkout root is resolved via PEP 610
    ``direct_url.json`` instead.
    """

    package_dir = Path(__file__).resolve().parent
    bundled = package_dir / "_data"
    if bundled.is_dir():
        return bundled
    from .provenance import source_root

    return source_root()


__all__ = ("resource_root",)
