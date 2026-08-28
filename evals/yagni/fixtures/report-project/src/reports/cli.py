from .export import ExporterRegistry


ENABLE_FUTURE_FORMATS = False


def run_export(format_name: str, rows: list[tuple[str, int]]) -> str | bytes:
    exporter = ExporterRegistry().formats[format_name]
    return exporter(rows)
