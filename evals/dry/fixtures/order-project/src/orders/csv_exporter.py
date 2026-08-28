import csv
import io


class CsvOrderExporter:
    """Render the stable public order CSV contract."""

    def render(self, rows: list[tuple[str, str, int]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(("id", "status", "total"))
        writer.writerows(rows)
        return output.getvalue()
