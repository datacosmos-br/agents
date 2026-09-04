import pytest
from reports.export import export_csv


def test_csv_is_the_supported_contract() -> None:
    assert export_csv([("north", 7)]) == "name,total\nnorth,7\n"


def test_csv_preserves_raw_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "csv.writer", lambda _output, **_kwargs: (_ for _ in ()).throw(OSError("disk"))
    )
    with pytest.raises(OSError, match="disk"):
        export_csv([])
