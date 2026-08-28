# Policy project law

- `config/delivery-policy.toml` is the only writable owner of channel timeouts.
- `tools/render_policy.py` is the only supported projection writer.
- `src/delivery/generated_policy.py` is generated and must never be hand-edited.
- Public runtime: `python -m delivery.cli email`.
- Native gates: `python tools/render_policy.py --check` and
  `pytest tests/test_delivery.py`.
