import csv
import io


class ExportError(RuntimeError):
    """The requested supported export failed."""


class ExporterRegistry:
    def __init__(self) -> None:
        self.formats = {"csv": export_csv, "pdf": export_pdf, "xml": export_xml}


def export_csv(rows: list[tuple[str, int]]) -> str:
    output = io.StringIO()
    try:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(("name", "total"))
        writer.writerows(rows)
        return output.getvalue()
    except (csv.Error, OSError) as error:
        raise ExportError("CSV export failed") from error


def export_pdf(rows: list[tuple[str, int]]) -> bytes:
    raise NotImplementedError("future PDF renderer")


def export_xml(rows: list[tuple[str, int]]) -> str:
    raise NotImplementedError("future XML renderer")
