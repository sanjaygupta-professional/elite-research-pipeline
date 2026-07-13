# The Cinnabar Dispatch — Insight-First Redesign (Design)

- **Date:** 2026-07-13
- **Status:** Approved design, entering implementation
- **Author:** Sanjay Gupta (with Claude)
- **Scope:** `digest/` (Astro). Presentation, structure, and modality only.

## 1. Context and problem

The weekly digest ("The Cinnabar Dispatch") is the public-facing artifact of
the Possibilities-with-Probabilities futures-intelligence system. An impeccable
`critique` scored the current page **19/40 on Nielsen's heuristics**: strong
typographic craft and editorial voice, but a mediocre *interface*. It treats the
reader as a linear-reading desktop visitor, when PRODUCT.md says the reader is
signal-poor, mobile, between meetings, and sometimes on assistive tech.

The mandate: make the digest **10x better on presentation, accessibility, and
modality, without changing a single word of written content**, and without
abandoning the design system the reader already likes.

Verified findings driving this work:

- The 5-dimension signal profile is declared "the product" in DESIGN.md but
  renders as an undecodable code string (`E3 T-Ac U3 H-Gr Z-Now`). Worst
  recognition-not-recall failure in the most important place.
- **Cinnabar on cream measures 4.15:1** (computed OKLCH to sRGB to WCAG). It
  fails AA for normal text (needs 4.5:1); it is used at 12px labels.
  `--color-cinnabar-deep` measures **6.40:1** and passes.
- No skip link (WCAG 2.4.1 Level A fail); `<header>`/`<footer>` nested inside
  `<main>` so they lose their landmark roles; Synthesis and AudioBrief have no
  headings; audio has no transcript (WCAG 1.2.1 Level A fail).
- Linear-only structure: no skim path for a between-meetings reader.

## 2. Locked decisions

| Decision | Choice |
|---|---|
| Priority lane | Presentation and modality first; a11y foundation baked in (free during a structural rebuild) |
| IA backbone | **A — Insight-first briefing** |
| Profile viz | **Fingerprint glyph** in the index; labeled meters in the expanded detail |
| Audio | Transcript now + elevated player; per-signal chapters deferred |
| Dark theme | Auto, via `prefers-color-scheme` |
| Share / distribution | Share-a-signal (copy formatted quote) + RSS feed |
| "Expand on demand" | Jump links to detail that is **always rendered** (no collapse, no JS state) |

## 3. Invariants (non-goals)

1. **No content changes.** Not one word of thesis, synthesis, signal prose,
   audio script, or sources. A content diff must show zero copy edits.
2. **Design system stays.** Warm cream + deep ink + cinnabar (One Voice Rule).
   Geist Mono display + Bricolage body. Thesis stays the single display element
   (One-Display-Per-View). Flat-by-default. Motion 120-220ms ease-out.
3. **Scan automation not disrupted.** The weekly scan regenerates
   `index.astro` from the prior issue as a template. New structure must be
   "copy-forward safe," and the scan prompt must co-evolve in lockstep (§9).
4. **Citation standard preserved.** Full-domain source labels, mono audit trail.

## 4. Information architecture (backbone A)

New top-to-bottom order (rationale in brackets):

1. **Masthead** — unchanged. [orientation]
2. **Thesis (HeroThesis)** — unchanged, stays the hero. [the argument first]
3. **Audio brief + transcript** — elevated directly under the thesis.
   [the one modality that works in transit; offered early]
4. **The pattern this week** — the existing ClusterCallout insight, **moved up**
   from the page foot to right after the audio. Not duplicated at the bottom.
   [lead with the synthesized insight, per the chosen backbone]
5. **Signals this week (index)** — a scannable list: index number + fingerprint
   glyph + one-line title + strong/weak label + jump link to detail.
   [the skim path a between-meetings reader needs]
6. **Synthesis** — the three-paragraph analysis, retained, now with a heading.
   [full argument, for those who read on]
7. **Signal detail (x5)** — always rendered; jump targets from the index; each
   with the labeled-meter profile, why/watch, sources, and a share action.
8. **Methodology** — unchanged.
9. **Previous issues** — unchanged (already a component).

A slim, non-intrusive "back to signals" affordance appears after the first
signal detail on scroll (in-page nav return path). It respects
`prefers-reduced-motion` and is keyboard reachable.

## 5. Signal-profile fingerprint glyph

The centerpiece. Same data, radically more legible, still mono, still
accessible.

**Data model.** Two magnitudes and three ordered positions:

- `E` Evidence 1-5 (magnitude, fill x/5)
- `U` Capability Unlock 1-4 (magnitude, fill x/4)
- `T` Trajectory: Emerging < Accelerating < Maturing < Shifting (position 1-4)
- `H` Hype-Reality: Grounded < Ahead < Peak-hype < Post-hype (position 1-4)
- `Z` Horizon: Now < Near < Medium < Far (position 1-4)

A radar/pentagon is rejected: three of five axes are categorical positions, not
magnitudes, so a spider chart would imply false magnitude.

**Index form (compact).** Five mini vertical bars labeled `E T U H Z`. Bar
height encodes value (magnitude for E/U; position for T/H/Z). The exact value
prints beneath each bar in mono (`3 Ac 3 Gr Now`). Each signal reads as a
distinct silhouette, comparable down the column at a glance.

**Detail form (labeled meters).** In the expanded signal, the same profile
renders as five labeled rows: `Evidence  ###.. 3/5`, `Trajectory  --O-- Accelerating`,
etc. This is self-decoding and **replaces the need for a separate glossary** —
it resolves the P0 recognition gap directly.

**Accessibility.** Color is never the sole signal: value is carried by (a) bar
height, (b) the printed mono value, and (c) an `aria-label` on the glyph that
reads the full decoded profile ("Evidence 3 of 5, trajectory accelerating, ..."
). The visual bars are `aria-hidden`; the label carries the meaning to AT.

**Implementation.** New `SignalProfile.astro` component, driven by parsing the
existing `profile` string (e.g. `"E3 T-Ac U3 H-Gr Z-Now"`) so **no content or
prop shape changes** are required in the issue pages. A small pure parser maps
tokens to {label, value, max, kind}. Rendered with CSS (no images), mono type,
cinnabar-deep fills for AA contrast.

## 6. Modalities

**Audio transcript + elevated player.** The transcript already exists as prose
in `digest/audio-scripts/<date>.md`. Render it (build-time read, same pattern as
PreviousIssues) behind a "Read the transcript" `<details>` beside the elevated
player. Satisfies WCAG 1.2.1; gives open-plan readers and quote-seekers a text
path. Fix the player a11y at the same time (§7).

**Share-a-signal.** A copy button on each signal detail. On click, writes a
formatted quote block to the clipboard: signal title + decoded profile +
"what to watch" one-liner + deep link (`.../issues/<date>/#signal-N`). Uses the
async Clipboard API with a graceful fallback and a transient "copied"
confirmation. No content is authored; it composes existing fields.

**Dark theme (auto).** All palette values are CSS custom properties on `:root`.
Add a `@media (prefers-color-scheme: dark)` block that swaps ground and ink and
re-tunes cinnabar lightness for dark-mode AA. **Contrast must be recomputed for
the dark palette** (same OKLCH-to-WCAG method) before shipping. No toggle UI, no
persistence.

**RSS.** An Astro endpoint at `digest/src/pages/rss.xml.ts` using
`@astrojs/rss`, generated from `issues.json` + each issue's `description`. One
small file; slots the dispatch into feed readers the audience already uses.

## 7. Accessibility foundation (baked in)

| Fix | WCAG | Where |
|---|---|---|
| Skip link to `#main-content` | 2.4.1 (A) | `Issue.astro` + `global.css` |
| Hoist `<header>`/`<footer>` out of `<main>`; add `<nav>` for the index | 1.3.1 (A) | `Issue.astro`, index, Masthead |
| Visually-hidden headings on Audio, Insight, Synthesis | 1.3.1 / 2.4.6 | those components + `.visually-hidden` util |
| Cinnabar text < 18px uses `--color-cinnabar-deep` (6.40:1) | 1.4.3 (AA) | `global.css` + components |
| Audio: `aria-label` on section, `alt=""` avatar, keep focus-visible outline | 1.1.1 / 2.4.7 | `AudioBrief.astro` |
| Transcript as text alternative | 1.2.1 (A) | new transcript block |
| Color not sole signal on profile | 1.4.1 (A) | `SignalProfile.astro` |
| `og:image` for social/link previews | n/a (quality) | `Issue.astro` |

## 8. Component and file change map

- **New:** `SignalProfile.astro` (glyph + meters), `SignalIndex.astro` (the
  scannable list), `Transcript.astro` (details/summary), `ShareSignal.astro`
  (copy button + inline script), `rss.xml.ts` (endpoint).
- **Modified:** `Issue.astro` (skip link, landmarks, og:image), `global.css`
  (dark theme, `.visually-hidden`, cinnabar-deep swaps, glyph tokens, dead-CSS
  removal), `index.astro` (reorder to backbone A, mount SignalIndex + moved
  ClusterCallout + SignalProfile + Transcript + ShareSignal), `Signal.astro`
  (labeled-meter profile, share action, heading), `AudioBrief.astro` (a11y +
  elevated placement), `Synthesis.astro` (heading), `ClusterCallout.astro`
  (heading; now mounted near top).
- **Migrated:** the 9 archived `issues/*.astro` pages to the new components,
  where mechanical and safe (§9 governs ordering).

## 9. Data flow and the scan-pipeline co-evolution (critical)

The weekly scan (`scripts/run-weekly-scan.sh` + `scripts/weekly-scan-prompt.md`
Step 9) rewrites `index.astro` each Monday by copying the prior issue's
structure and changing values. **If the structure changes and the prompt does
not, the next scan will regress the redesign** — exactly the class of bug that
hit the PreviousIssues swap.

Therefore:

- All new components are driven by the **existing** props and the existing
  `profile` string. No new per-signal content or prop shape is introduced, so
  the scan's authoring burden is unchanged.
- Step 9 of the prompt is rewritten in the same change set to describe the new
  component set and the new section order, with an explicit "do not reintroduce
  the old structure" guard (superseding the interim fix in PR #31, which is
  folded in here).
- The scan's dispatch-archiving `sed` path-fixups are re-verified against the
  new import list.

## 10. Phasing

- **Phase 1 — foundation + centerpiece:** `.visually-hidden`, skip link,
  landmarks, cinnabar-deep contrast swap, `SignalProfile` (glyph + meters),
  `SignalIndex`, IA reorder in `index.astro`.
- **Phase 2 — modalities:** transcript, share-a-signal, dark theme, RSS.
- **Phase 3 — durability:** scan-prompt Step 9 co-evolution, archived-issue
  migration, dead-CSS removal, contrast recompute for dark.

## 11. Testing and verification

- `npm run build` clean; CI `verify-digest` green.
- Recompute WCAG contrast for **both** themes with the OKLCH-to-WCAG script;
  every text token >= 4.5:1 (or >= 3:1 for >=18px/large).
- Keyboard-only pass: skip link works, index jump links work, share button and
  audio controls reachable, focus-visible everywhere.
- AT heading-navigation reaches Audio, Insight, Synthesis, and each signal.
- **Content diff gate:** `git diff` on rendered copy shows zero word changes.
- Cross-issue: an archived issue renders the same components as the current one.

## 12. Success criteria

1. WCAG AA on every text-on-background combination, in light and dark. Verified
   numerically, not by eye.
2. Re-run `impeccable critique`; Nielsen total improves from 19/40 to **>= 30/40**.
3. Zero content changes (diff gate passes).
4. `npm run build` and CI green; the next weekly scan reproduces the new
   structure (prompt co-evolved).

## 13. Risks and mitigations

- **Scan regression (high impact):** mitigated by §9 — prompt and template
  co-evolve; new components copy-forward safe.
- **Dark-mode contrast surprises:** mitigated by recompute-before-ship.
- **Scope creep toward audio-first / chapters:** explicitly deferred; YAGNI.
- **Archived-page churn:** migration is Phase 3 and gated on the current issue
  working first; archived pages degrade gracefully if left.

## 14. Open questions

- None blocking. Per-signal audio chapters and a manual dark-mode toggle are
  deferred, revisitable after this ships.
