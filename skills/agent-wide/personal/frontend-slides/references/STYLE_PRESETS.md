# Style Presets Reference

Curated visual styles for `frontend-slides`.

Use this file for:

- the mandatory viewport-fitting CSS base
- preset selection and mood mapping
- CSS gotchas and validation rules

Abstract shapes only. Avoid illustrations unless the user explicitly asks for them.

## Viewport Fit Is Non-Negotiable

Every slide must fully fit in one viewport.

### Golden Rule

```text
Each slide = exactly one viewport height.
Too much content = split into more slides.
Never scroll inside a slide.
```

### Density Limits

| Slide Type    | Maximum Content                           |
| ------------- | ----------------------------------------- |
| Title slide   | 1 heading + 1 subtitle + optional tagline |
| Content slide | 1 heading + 4-6 bullets or 2 paragraphs   |
| Feature grid  | 6 cards maximum                           |
| Code slide    | 8-10 lines maximum                        |
| Quote slide   | 1 quote + attribution                     |
| Image slide   | 1 image, ideally under 60vh               |

## Mandatory Base CSS

Use the canonical viewport-fitting rules in `BASE_CSS.md` (skill file).

## Viewport Checklist

- every `.slide` has `height: 100vh`, `height: 100dvh`, and `overflow: hidden`
- all typography uses `clamp()`
- all spacing uses `clamp()` or viewport units
- images have `max-height` constraints
- grids adapt with `auto-fit` + `minmax()`
- short-height breakpoints exist at `700px`, `600px`, and `500px`
- if anything feels cramped, split the slide

## Mood to Preset Mapping

| Mood                  | Good Presets                                       |
| --------------------- | -------------------------------------------------- |
| Impressed / Confident | Bold Signal, Electric Studio, Dark Botanical       |
| Excited / Energized   | Creative Voltage, Neon Cyber, Split Pastel         |
| Calm / Focused        | Notebook Tabs, Paper & Ink, Swiss Modern           |
| Inspired / Moved      | Dark Botanical, Vintage Editorial, Pastel Geometry |

## Preset Catalog

### 1. Bold Signal

- Vibe: confident, high-impact, keynote-ready
- Best for: pitch decks, launches, statements
- Fonts: Archivo Black + Space Grotesk
- Palette: charcoal base, hot orange focal card, crisp white text
- Signature: oversized section numbers, high-contrast card on dark field

### 2. Electric Studio

- Vibe: clean, bold, agency-polished
- Best for: client presentations, strategic reviews
- Fonts: Manrope only
- Palette: black, white, saturated cobalt accent
- Signature: two-panel split and sharp editorial alignment

### 3. Creative Voltage

- Vibe: energetic, retro-modern, playful confidence
- Best for: creative studios, brand work, product storytelling
- Fonts: Syne + Space Mono
- Palette: electric blue, neon yellow, deep navy
- Signature: halftone textures, badges, punchy contrast

### 4. Dark Botanical

- Vibe: elegant, premium, atmospheric
- Best for: luxury brands, thoughtful narratives, premium product decks
- Fonts: Cormorant + IBM Plex Sans
- Palette: near-black, warm ivory, blush, gold, terracotta
- Signature: blurred abstract circles, fine rules, restrained motion

### 5. Notebook Tabs

- Vibe: editorial, organized, tactile
- Best for: reports, reviews, structured storytelling
- Fonts: Bodoni Moda + DM Sans
- Palette: cream paper on charcoal with pastel tabs
- Signature: paper sheet, colored side tabs, binder details

### 6. Pastel Geometry

- Vibe: approachable, modern, friendly
- Best for: product overviews, onboarding, lighter brand decks
- Fonts: Plus Jakarta Sans only
- Palette: pale blue field, cream card, soft pink/mint/lavender accents
- Signature: vertical pills, rounded cards, soft shadows

### 7. Split Pastel

- Vibe: playful, modern, creative
- Best for: agency intros, workshops, portfolios
- Fonts: Outfit only
- Palette: peach + lavender split with mint badges
- Signature: split backdrop, rounded tags, light grid overlays

### 8. Vintage Editorial

- Vibe: witty, personality-driven, magazine-inspired
- Best for: personal brands, opinionated talks, storytelling
- Fonts: Fraunces + Work Sans
- Palette: cream, charcoal, dusty warm accents
- Signature: geometric accents, bordered callouts, punchy serif headlines

### 9. Neon Cyber

- Vibe: futuristic, techy, kinetic
- Best for: AI, infra, dev tools, future-of-X talks
- Fonts: Clash Display + Satoshi
- Palette: midnight navy, cyan, magenta
- Signature: glow, particles, grids, data-radar energy

### 10. Terminal Green

- Vibe: developer-focused, hacker-clean
- Best for: APIs, CLI tools, engineering demos
- Fonts: JetBrains Mono only
- Palette: GitHub dark + terminal green
- Signature: scan lines, command-line framing, precise monospace rhythm

### 11. Swiss Modern

- Vibe: minimal, precise, data-forward
- Best for: corporate, product strategy, analytics
- Fonts: Archivo + Nunito
- Palette: white, black, signal red
- Signature: visible grids, asymmetry, geometric discipline

### 12. Paper & Ink

- Vibe: literary, thoughtful, story-driven
- Best for: essays, keynote narratives, manifesto decks
- Fonts: Cormorant Garamond + Source Serif 4
- Palette: warm cream, charcoal, crimson accent
- Signature: pull quotes, drop caps, elegant rules

## Direct Selection Prompts

If the user already knows the style they want, let them pick directly from the preset
names above instead of forcing preview generation.

## Animation Feel Mapping

| Feeling                  | Motion Direction                                     |
| ------------------------ | ---------------------------------------------------- |
| Dramatic / Cinematic     | slow fades, parallax, large scale-ins                |
| Techy / Futuristic       | glow, particles, grid motion, scramble text          |
| Playful / Friendly       | springy easing, rounded shapes, floating motion      |
| Professional / Corporate | subtle 200-300ms transitions, clean slides           |
| Calm / Minimal           | very restrained movement, whitespace-first           |
| Editorial / Magazine     | strong hierarchy, staggered text and image interplay |

## CSS Gotcha: Negating Functions

Never write these:

```css
right: -clamp(28px, 3.5vw, 44px);
margin-left: -min(10vw, 100px);
```

Browsers ignore them silently.

Always write this instead:

```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));
margin-left: calc(-1 * min(10vw, 100px));
```

## Validation Sizes

Test at minimum:

- Desktop: `1920x1080`, `1440x900`, `1280x720`
- Tablet: `1024x768`, `768x1024`
- Mobile: `375x667`, `414x896`
- Landscape phone: `667x375`, `896x414`

## Anti-Patterns

Do not use:

- purple-on-white startup templates
- Inter / Roboto / Arial as the visual voice unless the user explicitly wants
  utilitarian neutrality
- bullet walls, tiny type, or code blocks that require scrolling
- decorative illustrations when abstract geometry would do the job better
