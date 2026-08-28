---
description: Complete workflow validation before the first external effect.
---

# Validate the complete workflow before effects

Load and validate every input, environment value, configuration owner, source,
destination, provider capability, external executable, authorization,
child-process contract, storage bound, ownership proof, and publication
condition required by the entire workflow before its first mutation or external
call.

Preflight is read-only and deterministic. Discovery performed after an effect,
lazy validation inside a mutation loop, and validate-as-you-go publication are
prohibited. If a prerequisite can change between preflight and effect, acquire
the declared ownership/serialization primitive before validating and retain it
through publication.
