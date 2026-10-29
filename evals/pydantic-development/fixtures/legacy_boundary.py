"""Legacy boundary under review: every construct below is a removal-catalog entry.

The task prompt asks for the maximal-Pydantic rewrite; this file is review input,
not running code.
"""

from __future__ import annotations

from typing import Literal, cast

import yaml

from flext_core import m, p, t


class FlextShippingModels:
    class Order(m.FrozenModel):
        lines: tuple[FlextShippingModels.Line, ...]  # sibling via its enclosing family
        status: Literal["open", "closed"]  # string domain instead of a c StrEnum

    class Line(m.FrozenModel):
        sku: str

    class Pipeline(m.FrozenModel):
        model_config = {"arbitrary_types_allowed": True}  # raw dict + global relaxation
        sink: p.ShipmentSink

    class Money(m.FrozenModel):
        amount: int

        def __eq__(self, other: object) -> bool:  # hand-written value equality
            return isinstance(other, FlextShippingModels.Money) and other.amount == self.amount


def load(path: str) -> FlextShippingModels.Order:
    raw = cast("t.JsonMapping", yaml.safe_load(open(path)))  # unvalidated loader output
    if isinstance(raw, dict) and raw.get("status") == "open":
        return FlextShippingModels.Order.model_validate(raw)
    order = FlextShippingModels.Order.model_validate(raw)
    return order.model_copy(update={"status": "closed"})  # unvalidated update


FlextShippingModels.Order.model_rebuild()
