# Deep Research procedure

## Deep Research

Produce thorough, cited research reports from multiple web sources using firecrawl and
exa MCP tools.

### When to Activate

- User asks to research any topic in depth
- Competitive analysis, technology evaluation, or market sizing
- Due diligence on companies, investors, or technologies
- Any question requiring synthesis from multiple sources
- User says "research", "deep dive", "investigate", or "what's the current state of"

### Research Tool Preflight

Select the complete declared research toolchain before searching. Validate every
required search, crawl, authentication, and publication capability before the first
network call. Firecrawl and Exa are supported when the active environment declares them;
failure of any selected tool stops research without switching to another provider or
reduced source set.

### Workflow

#### Step 1: Understand the Goal

Ask 1-2 quick clarifying questions:

- "What's your goal — learning, making a decision, or writing something?"
- "Any specific angle or depth you want?"

If the user says "just research it", proceed with the scope stated in the request and
disclose low-risk assumptions. Ask one targeted question before any missing
decision-critical input could change the research outcome.

#### Step 2: Plan the Research

Break the topic into 3-5 research sub-questions. Example:

- Topic: "Impact of AI on healthcare"
  - What are the main AI applications in healthcare today?
  - What clinical outcomes have been measured?
  - What are the regulatory challenges?
  - What companies are leading this space?
  - What's the market size and growth trajectory?

#### Step 3: Execute Multi-Source Search

For each sub-question, use every search tool selected during preflight:

**With firecrawl:**

```text
firecrawl_search(query: "<sub-question keywords>", limit: 8)
```

**With exa:**

```text
web_search_exa(query: "<sub-question keywords>", numResults: 8)
web_search_advanced_exa(query: "<keywords>", numResults: 5, startPublishedDate: "2025-01-01")
```

**Search strategy:**

- vary queries until each decision-critical facet has authoritative evidence
- mix source types only when the decision brief requires them
- Prioritize: academic, official, reputable news > blogs > forums

#### Step 4: Deep-Read Key Sources

For the most promising URLs, fetch full content:

**With firecrawl:**

```text
firecrawl_scrape(url: "<url>")
```

**With exa:**

```text
crawling_exa(url: "<url>", tokensNum: 5000)
```

Deep-read every source that supports a decision-critical claim. Do not rely only on
search snippets or stop at an arbitrary source quota.

#### Step 5: Synthesize and Write Report

Structure the report:

```markdown
# [Topic]: Research Report

_Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]_

## Executive Summary

[3-5 sentence overview of key findings]

## 1. [First Major Theme]

[Findings with inline citations]

- Key point ([Source Name](url))
- Supporting data ([Source Name](url))

## 2. [Second Major Theme]

...

## 3. [Third Major Theme]

...

## Key Takeaways

- [Actionable insight 1]
- [Actionable insight 2]
- [Actionable insight 3]

## Sources

1. [Title](url) — [one-line summary]
2. ...

## Methodology

Searched [N] queries across web and news. Analyzed [M] sources. Sub-questions
investigated: [list]
```

#### Step 6: Deliver

- **Short topics**: Post the full report in chat
- **Long reports**: publish a file only when the user requested a validated destination;
  otherwise deliver the complete report in the authorized response

### Quality Rules

1. **Every claim needs a source.** No unsourced assertions.
2. **Cross-reference.** If only one source says it, flag it as unverified.
3. **Recency matters.** Prefer sources from the last 12 months.
4. **Acknowledge gaps.** If you couldn't find good info on a sub-question, say so.
5. **No hallucination.** If you don't know, say "insufficient data found."
6. **Separate fact from inference.** Label estimates, projections, and opinions clearly.

### Examples

```text
"Research the current state of nuclear fusion energy"
"Deep dive into Rust vs Go for backend services in 2026"
"Research the best strategies for bootstrapping a SaaS business"
"What's happening with the US housing market right now?"
"Investigate the competitive landscape for AI code editors"
```
