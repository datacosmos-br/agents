---
description: Required process-environment validation without defaults or loaders.
---

# Required environment values are exact

Read required environment variables once at the typed boundary from the current
process environment. A variable that is absent, empty, whitespace-only,
conflicting with another owner, contains an unexpanded placeholder, violates
its schema, or is unauthorized raises immediately before effects.

Do not load a missing value from a file, shell profile, keyring, service,
alternate name, inherited compatibility alias, prompt, or operational default.
Do not silently trim, coerce, repair, or substitute it. Never print secret
values, derived fingerprints, or full environments in failure evidence.
