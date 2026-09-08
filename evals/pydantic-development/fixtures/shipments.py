"""Ingress boundary under review: external shipment records reach the fleet untyped."""

from __future__ import annotations

from typing import Any

import json


def parse_shipment(raw: str) -> dict[str, Any]:
    """Current legacy parser returning a raw mapping."""
    return json.loads(raw)
