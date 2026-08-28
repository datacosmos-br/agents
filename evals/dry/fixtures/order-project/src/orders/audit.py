from typing import Protocol


class AuditSink(Protocol):
    def emit(self, event: str, order_id: str) -> None: ...
