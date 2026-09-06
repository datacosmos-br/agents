# Brand Voice — Procedure

Build a durable voice profile from real source material, then use that profile everywhere instead of re-deriving style from scratch or defaulting to generic AI copy.

## When to Activate

- the user wants content or outreach in a specific voice
- writing for X, LinkedIn, email, launch posts, threads, or product updates
- adapting a known author's tone across channels
- the existing content lane needs a reusable style system instead of one-off mimicry

## Source Priority

Use the strongest real source set available, in this order:

1. recent original X posts and threads
2. articles, essays, memos, launch notes, or newsletters
3. real outbound emails or DMs that worked
4. product docs, changelogs, README framing, and site copy

Do not use generic platform exemplars as source material.

## Collection Workflow

1. Require a representative source set before producing a profile; missing
   evidence blocks profile creation instead of selecting generic examples.
2. Gather 5 to 20 representative samples when available.
3. Prefer recent material over old material unless the user says the older writing is more canonical.
4. Separate "public launch voice" from "private working voice" if the source set clearly splits.
5. Use `x-api` only when selected before collection and its availability and
   authorization pass preflight; its failure ends collection.
6. If site copy matters, include the current product site and repository framing.

## What to Extract

- rhythm and sentence length
- compression vs explanation
- capitalization norms
- parenthetical use
- question frequency and purpose
- how sharply claims are made
- how often numbers, mechanisms, or receipts show up
- how transitions work
- what the author never does

## Output Contract

Produce a reusable `VOICE PROFILE` block that downstream skills can consume directly. Use the schema in `references/voice-profile-schema.md` (skill file).

Keep the profile structured and short enough to reuse in session context. The point is not literary criticism. The point is operational reuse.

## Hard Bans

Delete and rewrite any of these:

- fake curiosity hooks
- "not X, just Y"
- "no fluff"
- forced lowercase
- LinkedIn thought-leader cadence
- bait questions
- "Excited to share"
- generic founder-journey filler
- corny parentheticals

## Persistence Rules

- Reuse a confirmed `VOICE PROFILE` only while its declared source set remains
  current for the task.
- If the user asks for a durable artifact, validate the destination and complete
  profile before publishing it atomically in the requested workspace location.
- Do not create repo-tracked files that store personal voice fingerprints unless the user explicitly asks for that.

## Downstream Use

Use this skill before or inside:

- `content-engine`
- `crosspost`
- article or launch writing
- cold or warm outbound across X, LinkedIn, and email

If another skill has an incomplete voice capture section, this skill remains the
single canonical profile owner.
