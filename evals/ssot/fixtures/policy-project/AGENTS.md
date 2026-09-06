# Policy project law

- `config/delivery-policy.toml` is the only writable owner of channel timeouts.
- The root `make gen APPLY=Y` verb is the only supported generator facade.
- `src/delivery/generated_policy.py` is generated and must never be hand-edited.
- Public runtime: `make runtime APPLY=Y`.
- Native gates: `make check APPLY=Y`, `make test APPLY=Y`, and
  `make test-full APPLY=Y`.
