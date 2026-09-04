---
globs: **/*.py
---

# Errors propagate loud; no shims, accessors, or fallbacks

Never swallow, mask, or paper over a failure. No fallback that invents or
defaults data, no compatibility shim/alias, no silent default. Errors always
`raise` or `r.fail(...)`.

- No `get_`/`set_` accessor boilerplate — use direct attributes, computed
  properties, or models.
- No loose helpers outside the `u.*` utilities facade; shared behavior lives in
  approved layers via MRO. No bare `except:` / `except: pass`.
