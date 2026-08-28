---
description: Mandatory fail-loud execution protocol for every project workflow.
---

# Strict execution is universal and non-optional

Every project and projected agent applies all of these policies together:

- [fail loud](fail-loud.md);
- [no fallback](no-fallback.md);
- [preflight before effects](preflight-before-effects.md);
- [required environment](required-environment.md);
- [atomic effects](atomic-effects.md);
- [causal subprocess propagation](causal-subprocess.md);
- [no keyring](no-keyring.md);
- [zero residue](zero-residue.md).

The policies are cumulative. A project rule may make them narrower or reject
more inputs; it cannot relax, catch, normalize, skip, defer, or route around any
of them. Existing opposing behavior is a blocking violation to exterminate at
its owner, never grandfathered compatibility.

Resolve gate applicability before invocation. A dormant external-token gate is
not executed; selecting or invoking it applies every policy above.
