"""Model with a broken declaration and a teammate proposal under review.

The forward reference below does not resolve at import: the class declares its
own name through ``child`` while the module freezes before ``Node`` exists, so
any default rebuild shortcut proposed against it is a violation reviewed by the
task prompt rather than running code here.
"""

from __future__ import annotations

from flext_core import m


class Node(m.FrozenModel):
    """Node whose forward reference fails to resolve at import."""

    child: Node | None = None
