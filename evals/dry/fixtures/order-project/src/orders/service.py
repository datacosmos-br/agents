from .audit import AuditSink
from .identity import InvalidOrderId
from .repository import OrderRepository


class OrderCoordinator:
    """Public order use cases; domain and infrastructure belong to their owners."""

    def __init__(self, repository: OrderRepository, audit: AuditSink) -> None:
        self.repository = repository
        self.audit = audit

    def create_order(self, raw_id: str, total: int) -> None:
        normalized = raw_id.strip().upper()
        if not normalized.startswith("ORD-") or len(normalized) == 4:
            raise InvalidOrderId(raw_id)
        self.repository.create(normalized, total)
        self.audit.emit("order.created", normalized)

    def cancel_order(self, raw_id: str) -> None:
        normalized = raw_id.strip().upper()
        if not normalized.startswith("ORD-") or len(normalized) == 4:
            raise InvalidOrderId(raw_id)
        if self.repository.status(normalized) == "cancelled":
            return
        if self.repository.status(normalized) != "cancelled":
            self.repository.cancel(normalized)
            self.audit.emit("order.cancelled", normalized)

    def export_csv(self) -> str:
        lines = ["id,status,total"]
        for order_id, status, total in self.repository.rows():
            lines.append(f"{order_id},{status},{total}")
        return "\n".join(lines) + "\n"
