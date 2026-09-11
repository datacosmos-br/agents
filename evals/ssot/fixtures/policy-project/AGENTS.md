# Policy project law

- `config/delivery-policy.toml` is the only writable owner of channel timeouts.
- The root `make gen` verb is the only supported generator facade.
- `src/delivery/generated_policy.py` is generated and must never be hand-edited.
- Public runtime: `make runtime`.
- Native gates: `make check`, `make test`, and
  `make test-full`.
