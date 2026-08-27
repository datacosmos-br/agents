"""Test fixtures that obey repository-local scratch policy."""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path(
    tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
) -> Iterator[Path]:
    """Create one deterministic test directory without pytest's current symlink."""

    identity = hashlib.sha256(request.node.nodeid.encode()).hexdigest()
    owned = tmp_path_factory.mktemp(f"case-{identity}", numbered=False)
    yield owned
    shutil.rmtree(owned)
