# CRM project rules

- `src/crm/models.py` owns the domain models. `make gen` writes `src/crm/protocols.py`
  from them, one protocol per model mirroring its bases and own fields; never edit it.
- External input is validated once, in `src/crm/api.py`. No other repository imports
  `crm`.
- Prove behavior with `make runtime`, which parses `samples/customer.json` through
  `crm.api` and prints `crm.export` output; then run `make check` and `make test`.
