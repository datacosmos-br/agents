# Scanner finding

Semgrep rule `python.lang.security.audit.subprocess-shell-true` reports
`src/exporter.py:41`: untrusted `format_name` is interpolated into a command
executed with `shell=True`. `Exporter.render` owns the operation. The project
already exposes an argument-vector renderer and its native security target is
`make security`. The dependency scan reports no known vulnerability in that
renderer dependency; the exploitable attack surface is the local shell call. No
triage decision or suppression exists.
