"""PEP 610 provenance: resolve version and source identity from installed metadata.

For a release wheel the distribution version equals the GitHub tag.  For an
editable / development install, ``direct_url.json`` records the source checkout
as a ``file://`` URL with ``dir_info.editable = true``.
"""

from __future__ import annotations

import json
from importlib.metadata import distribution
from pathlib import Path
from urllib.parse import unquote, urlparse

_PACKAGE = "agents-governance"


def version() -> str:
    """Return the installed distribution version (= release tag)."""

    return distribution(_PACKAGE).version


def source_url() -> str | None:
    """Return the PEP 610 ``direct_url.json`` source URL, if recorded."""

    direct_url_text = distribution(_PACKAGE).read_text("direct_url.json")
    if direct_url_text is None:
        return None
    data = json.loads(direct_url_text)
    return data.get("url")


def source_root() -> Path:
    """Return the physical source root for an editable / development install.

    A release wheel never reaches this path because :func:`resources.resource_root`
    returns the bundled ``_data`` directory first.  This function is only the
    fallback for editable installs, where ``direct_url.json`` must record a
    ``file://`` source with ``dir_info.editable = true``.
    """

    direct_url_text = distribution(_PACKAGE).read_text("direct_url.json")
    if direct_url_text is None:
        raise ValueError(
            "agents-governance installation has no PEP 610 direct_url.json"
        )
    direct_url = json.loads(direct_url_text)
    directory_info = direct_url.get("dir_info")
    if (
        not isinstance(directory_info, dict)
        or directory_info.get("editable") is not True
    ):
        raise ValueError(
            "agents-governance must be installed from an editable source "
            "checkout or a release wheel"
        )
    parsed = urlparse(direct_url["url"])
    if parsed.scheme != "file":
        raise ValueError("agents-governance editable source must use a file URL")
    return Path(unquote(parsed.path)).resolve(strict=True)


__all__ = ("source_root", "source_url", "version")
