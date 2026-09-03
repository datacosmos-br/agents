# dry-refactoring — extraction strategies

**Extract function** — the duplicate is a block of logic: move it to one
shared function called from both sites.

**Extract module/utility** — the duplicate spans files in different domains:
move shared logic to a utility file and import it.

**Extract constant or config** — repeated data or configuration.

**Template/base class** — structural duplication (repeated class shape).

Always:

- update all call sites, not just the two jscpd reported;
- keep tests passing after the refactoring;
- give the extracted abstraction a clear, descriptive name.
