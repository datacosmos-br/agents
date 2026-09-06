# Parser behavior contract

Public behavior: `parse_limit("25")` returns 25; `parse_limit("0")`, negative
numbers, non-numeric input, and values above 100 return `InvalidLimit` without
side effects. Current runtime incorrectly accepts 0. Owner: `parse_limit`.
Canonical regression command: `make test APPLY=Y`.
