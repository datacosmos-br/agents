# Report architecture

`export_csv` is the canonical owner for the only current report format. The CLI is its
sole current consumer. There is no plugin contract, remote renderer, format registry,
PDF/XML acceptance criterion, or compatibility commitment.
