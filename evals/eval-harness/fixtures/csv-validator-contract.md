# CSV validator capability

Input: a UTF-8 CSV file with headers `id,email`.

Required behavior:

- valid rows produce `report.json` with `accepted_count` and `rejected_count`;
- malformed email rows are rejected with their one-based row number;
- a missing `email` header exits with code 2 and creates no report;
- the existing valid-file behavior must remain unchanged.

Reliability target: capability pass@3 above 90%; regression pass^3 equals 100%.
