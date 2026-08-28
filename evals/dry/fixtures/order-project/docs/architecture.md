# Order module architecture

`OrderCoordinator` is a thin public orchestrator. `OrderId` exclusively owns
identifier parsing, `OrderRepository` owns persistence, `CsvOrderExporter` owns
CSV formatting, and `AuditSink` owns mutation audit events. Domain behavior must
not be copied into the orchestrator.
