# Policy project law

- `config/retry-policy.toml` is the only writable owner of retry values.
- `tools/render_policy.py` is the only supported projection writer.
- `src/retries/generated_policy.py` is generated and must never be hand-edited.
- Public runtime: `python -m retries.cli email`.
- Native gates: `python tools/render_policy.py --check` and
  `pytest tests/test_worker.py`.
