"""Model with a broken declaration and a normalizing caller under review."""

from __future__ import annotations

from flext_core import m


class Node(m.FrozenModel):
    """Node whose forward reference fails to resolve at import."""

    child: Node | None = None


def load(raw: str) -> Node | None:
    """Teammate proposal: rebuild the model and swallow validation failures."""
    try:
        Node.model_rebuild(_types_namespace={"Node": Node})
        return Node.model_validate_json(raw)
    except Exception:
        return None
