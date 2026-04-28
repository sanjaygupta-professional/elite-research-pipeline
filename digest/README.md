# The Cinnabar Dispatch

Astro static site at `/digest/` for the **Possibilities with Probabilities** weekly executive dispatch.

Designed via the `/impeccable` flow. Strategy and visual system locked in [`PRODUCT.md`](../PRODUCT.md) and [`DESIGN.md`](../DESIGN.md). Implementation brief at [`docs/plans/2026-04-28-executive-digest-shape-brief.md`](../docs/plans/2026-04-28-executive-digest-shape-brief.md).

## Develop

```bash
npm install
npm run dev          # http://localhost:4321/elite-research-pipeline/digest/
npm run build        # static output to dist/
npm run preview      # preview the production build
```

## Project layout

```
digest/
├── src/
│   ├── styles/global.css          Design tokens (OKLCH), type, motion
│   ├── layouts/Issue.astro        Page shell, font preconnect, meta
│   ├── components/
│   │   ├── Masthead.astro         Mono publication line, date, scan, counts
│   │   ├── HeroThesis.astro       Cinnabar rule + display thesis
│   │   ├── Synthesis.astro        Body prose paragraphs
│   │   ├── Signal.astro           One signal block: head, body, watch, sources
│   │   ├── ClusterCallout.astro   Inverted callout (deep ink + cream)
│   │   └── Methodology.astro      Footer line + author attribution
│   └── pages/index.astro          The 2026-04-27 issue
├── astro.config.mjs               base: /elite-research-pipeline/digest
├── package.json
└── tsconfig.json
```

## Design system (load-bearing)

The design tokens in `src/styles/global.css` are the canonical source of truth for typography, color, spacing, and motion. Edits should keep parity with `DESIGN.md`. Rules to remember:

- **The One Voice Rule**: cinnabar is the only chromatic actor. No second accent.
- **The 30-to-60 Rule**: cinnabar occupies between 30 and 60 percent of the visible surface.
- **The Audit-Trail Rule**: signal profiles, dates, source citations, and methodology line render in monospace.
- **The One-Display-Per-View Rule**: display weight appears exactly once per landed page.
- **The Flat-By-Default Rule**: surfaces are flat at rest. No `box-shadow` decoration.
- **No em-dashes** in any rendered copy.

## Typography

- **Display + body**: [Bricolage Grotesque](https://fonts.google.com/specimen/Bricolage+Grotesque) (variable, optical-size axis)
- **Mono**: [Geist Mono](https://fonts.google.com/specimen/Geist+Mono)

Both loaded from Google Fonts via CSS `@import` in `global.css`. Self-hosting is a future optimization if Google Fonts becomes a bottleneck.

## Deployment

Wired into `.github/workflows/deploy-docs.yml`. On every push to `master` that touches `digest/**`, `knowledge-system/**`, or `mkdocs.yml`, the workflow:

1. Builds MkDocs into `site/`
2. Installs digest dependencies (`npm ci`) and runs `npm run build`
3. Copies `digest/dist/*` into `site/digest/`
4. Uploads the merged `site/` as the GitHub Pages artifact

Live URL once deployed: https://sanjaygupta-professional.github.io/elite-research-pipeline/digest/.

## Adding a new issue

Currently `src/pages/index.astro` is the latest issue. Future architecture: move issues to a content collection at `src/content/issues/<date>.md`, create dynamic route `src/pages/[date].astro` and an archive index at `src/pages/index.astro`.

## Constraints

- Tested against Chrome/Chromium. OKLCH and CSS Color Module 4 are required (95%+ browser support as of 2026).
- `prefers-reduced-motion` respected globally.
- WCAG AA contrast on all text-on-color combinations.
