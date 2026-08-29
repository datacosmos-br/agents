# Project Documentation procedure

# Project Documentation

Conventions for writing, editing, restructuring, or reviewing documentation across every project under management. Applies whenever you touch anything in `docs/` (pages, tutorials, guides, reference, ADRs, concept pages, diagrams, navigation), `AGENTS.md`, `README.md`, or prose about project architecture — even when the request is just "fix the docs", "write a docs page", "the docs are wrong/confusing", "rename X across the docs", or an edit to a file under `docs/`. Defines the canonical project model, required terminology, prose / emphasis / diagram conventions, information architecture, the rule that generated docs are edited at their source, and the gates to run before docs work is done.

Adapted from Gas City upstream for multi-project use. Where the upstream references Gas City-specific primitives (six primitives, Mintlify, `docs/docs.json`), treat them as **the local project's equivalents** (`AGENTS.md` governance, docs site config, README map).

## 1. The canonical model

Every managed project has a **governance model** — the set of authoritative primitives that define how the project works. Teach it consistently and link to the canonical page rather than re-explaining it.

For Gas City projects, the model is six primitives:

| Primitive | Role | Derived terms that live *under* it (not co-equal) |
|---|---|---|
| **Agent** | WHO does the work | session, provider, pool |
| **Bead** | WHAT the work is | convoy, dependencies |
| **Formula** | HOW the work is done | run, sling, order |
| **Rig** | WHERE the work happens | repo, bead namespace, scope |
| **Pack** | what CONFIGURES the system | the City is the local (root) pack |
| **Event** | how you OBSERVE the system | (the "bus" is delivery machinery) |

For non-Gas City projects, use that project's own authoritative model (e.g. ai-hub's `AGENTS.md` + `config/governance.json` guarantees). The principle is the same: **one canonical page owns the model; every other page links to it.**

Relationship backbone (Gas City): packs declare agents/formulas/orders → the local pack is the City → a Formula operates over a convoy of Beads, fanning work to Agents that execute in a Rig → an Order automates *when* a formula runs → Events fire so humans and agents can observe.

## 2. Required terminology

When a term is settled, use the left column; never the right (except literal exceptions noted).

| Use this | Not this | Notes |
|---|---|---|
| **orchestrator** | "controller" | The conceptual component that executes formulas. Keep "controller" only in literal program output, JSON fields, and config keys — never in concept prose. |
| **platform** | "SDK" | Keep "SDK" only in literal output (e.g. `Welcome to Gas City SDK!`) and when it means a *different* SDK ("provider SDKs"). |
| **formulas v2** is the value | "graph.v2"; "legacy" | v2 = the orchestrator running a formula graph across many agents. v1 is a supported single-agent peer — never call it "legacy". |
| a **formula** is the *how* (a method over a convoy of beads) | "a formula is the work" | Beads are the work; the formula is the method. Never conflate. |
| **Events are fired** so humans/agents can observe | "events observe" | Events are the outbound notification, not an active observer. |

When you rename a concept across the corpus, see [references/terminology.md](../references/terminology.md) for the prose-vs-literal discipline (rename the concept in prose; preserve literal program output, JSON fields, config keys, and generated files).

## 3. Content stance

- **Docs are not the project's history.** No code archaeology on user pages — no `internal/*` package paths, no "the X subsystem was removed in the Y migration", no "the former Z". That belongs in `engdocs/`/`AGENTS.md`/ADRs. Migration framing is allowed only on an explicit migration page.
- **Motivate before you mechanize.** Lead a page with the problem it solves, then the solution, then the mechanics. Don't open on vocabulary.
- **Lead with the value.** Frame the project's value before its mechanics. Never frame orchestration or governance as a "thin layer."
- **One concrete image beats three abstract sentences.** Where you assert a capability, show a tangible instance of it.

## 4. Information architecture

Recommended nav sections are **Getting Started, Tutorials, Guides, Troubleshooting, Reference** (contributor map lives in `engdocs/` or `docs/contributors/`).

- **Every section has an Overview page** that introduces the section and lists every page beneath it with a one-line summary and a link.
- One page, one purpose. A page that tries to teach *and* specify does neither — split it and cross-link.
- The **repository/codebase map belongs in the README**, not in `docs/`.
- Concept material is unified on the canonical "how it works" page; don't reintroduce a separate "concepts" section.

## 5. Prose doctrine — cut words, sharpen points

Most bloat is information stored in the wrong medium. Move it to a cheaper carrier, then delete what isn't pulling weight. Every page must **stand alone**.

**Convert** (move load off prose):
- A relationship or sequence → a **diagram** (reuse an existing one or author a new one).
- A set of parallel options/fields/comparisons → a **table**.
- "you do X, which does Y" narration → an **annotated CLI/TOML snippet**.
- Edge cases and deep mechanics → an `<Accordion>`, or move them to a spec/reference page.

**Delete** (the load was fake): throat-clearing openers, hedge chains, restatement, narrating an artifact a snippet or table already shows, and adjectives standing in for evidence.

**Write for the reader, not about the edit.** No meta-commentary, no asides that only make sense relative to text you removed.

When you're running a deliberate **simplification pass** over a page or a whole section, follow [references/simplification.md](../references/simplification.md): the per-page loop (measure → convert/delete → verify), and the two guardrails — a **loss-check** and a **fact-check**.

## 6. Emphasis and formatting

- **Bold** *names a term*, on first mention only. *Italic* marks a *property or contrast*. Keep it to ~1–2 marks per paragraph.
- No body `# H1` — the frontmatter `title` is the H1. Use `##`/`###` in the body.
- Use root-relative links without the file extension, valid MDX where applicable.

## 7. Diagrams

Author the source, render with the project's diagram tooling, use the shared palette, and embed with **descriptive alt text**.

Two non-negotiables:
- **Keep labels short and let them fit** — a two-line "Name / role" beats a long sentence crammed in a box.
- Prefer reusing an existing rendered diagram over authoring a new one.

## 8. Generated content is edited at its source

Never hand-edit a generated file. To change wording in generated reference docs, edit the source that generates them and regenerate, then commit source + regenerated output together. A freshness test fails if they drift.

## 9. Verify before you call it done

Run the gates in [references/verification.md](../references/verification.md). Durable repo gates typically include nav↔file consistency, local markdown link checks, diagram re-rendering, and generated-doc freshness. Beyond the gates: every TOML/YAML fence must parse, every internal link and anchor must resolve, no page is orphaned from the nav, and no body H1 was introduced.

When you **move or remove a page**: add a redirect from the old path, rewrite inbound links, and update any nav/IA references.

## 10. Review and commit discipline

- **Author → the user reviews → commit only on explicit approval.** Push nothing without a clear go-ahead. This matters most for **diagrams and images**, which can't be reviewed in a text diff.
- Group commits by audience for reviewability: contributor (`AGENTS.md` + `engdocs/`) separate from user docs (`docs/`).
