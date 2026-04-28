<!-- SEED — re-run /impeccable document once there's code to capture the actual tokens and components. -->
---
name: Possibilities with Probabilities
description: A futures intelligence brand at the intersection of AI / GenAI and organizational transformation.
---

# Design System: Possibilities with Probabilities

## 1. Overview

**Creative North Star: "The Cinnabar Dispatch."**

A field report from someone watching the frontier of AI and organizational transformation, set in cinnabar ink on warm cream, typeset like a research dispatch. The page reads as **a considered communiqué**, not a news feed. The reader feels they have arrived at the desk of a sharp peer who has just finished thinking, has staked a position, and has shown the working.

The tonal anchor is editorial confidence: *The Generalist*'s thesis-driven framing, *a16z Future*'s willingness to say "your map is wrong and here is why," and *Stripe Press*'s research-grade typographic craft. Three references, one register: serious work that takes itself seriously without taking itself solemnly.

The system explicitly rejects three aesthetics: **MBB corporate slick** (navy + gold, exhibit furniture, watermarked PDF chrome), **AI-startup gradient soup** (purple gradients, glassmorphism, identical card grids, hero-metric templates), and **the generic GitHub Pages docs look** (Material theme defaults, search-bar-dominant chrome, sidebar-and-content layouts that read as documentation rather than editorial). The current MkDocs Material site is the third anti-reference made literal. The redesign moves decisively away from it.

**Key Characteristics:**

- **Warm cream as ground, cinnabar as voice.** A single committed accent carries 30 to 60 percent of the surface in deliberate roles. No second accent. No gradient. The cream is the silence; the cinnabar is the speech.
- **Display sans plus monospace.** A confident sans for headlines and body, a high-craft monospace for signal profiles, dates, and tags. The mono is not decorative. It carries the audit trail.
- **Responsive, not choreographed.** State transitions only. No scroll-driven sequences. The page does not perform.
- **Print-grade rhythm at screen scale.** Generous vertical space between sections, asymmetric grid where useful, line lengths capped near 65 to 75ch. Whitespace is not absence; it is structure.
- **Probability is visible.** The 5-dimension signal profile (Evidence, Trajectory, Uncertainty, Horizon, Z-axis) is a typographic primitive, rendered in mono, never hidden in metadata.

## 2. Colors

The palette is **two colors plus tinted neutrals**: warm cream (the field), deep ink (the type), cinnabar (the signal). Every hex value lands in the implementation pass. The directional intent is locked here.

### Primary

- **Cinnabar Voice** *(value to be resolved during implementation; target around `oklch(58% 0.18 35)`)*: the single committed accent. Carries section rules, signal-strength chips, footnote markers, accent quotation, the strongest pull-quotes, and the call-to-action in any digest. Used at 30 to 60 percent of the surface across the page, with rest space sized to make the cinnabar feel inevitable rather than decorative.

### Neutral

- **Warm Cream** *(value to be resolved; target around `oklch(96% 0.01 85)`)*: the surface. Tinted toward the cinnabar hue at chroma 0.01 so it reads as deliberate, not as `#fff` by default. The page is set on this; no element wraps the body to "improve readability."
- **Deep Ink** *(value to be resolved; target around `oklch(15% 0.02 60)`)*: the type. Tinted, not pure black. Reads as warm authority, not laser-printer.
- **Cream-on-Cream Hairline** *(value to be resolved)*: a barely-perceptible tinted neutral one or two oklch lightness steps below the ground, reserved for full-width section rules and table separators where cinnabar would be too loud.

### Named Rules

**The One Voice Rule.** Cinnabar is the only chromatic actor on the page. There is no second accent, no complementary color, no neutral-with-personality. If a second hue is needed, the design is wrong. Find a typographic, scale, or layout solution instead.

**The Cream-Tints-Toward-Cinnabar Rule.** Every neutral is tinted at chroma 0.005 to 0.01 toward the cinnabar hue. Pure greys are forbidden. The page must feel chromatically of-a-piece even where no cinnabar element is present.

**The 30-to-60 Rule.** Cinnabar occupies between 30 and 60 percent of the visible surface on any landed page. Below 30 percent, the brand reads as restrained, which is the wrong register. Above 60 percent, it reads as drenched, which crowds out the type.

## 3. Typography

**Display Font:** Geist Mono at display sizes (weight 600, tracking -0.04em). The brutalist move: the brand's primary display face is monospace. Mono carries the headline.

**Body Font:** Bricolage Grotesque (variable, optical-size axis at 14 for body). Warm humanist proportional sans for long reading.

**Mono Font:** Geist Mono. Used at body weight for the audit trail (signal profiles, dates, source citations, methodology line) and at display weight for headlines.

**Character.** The pairing reads as a research dispatch from a writer who respects type, where the typewriter cadence of mono carries argument and the proportional sans carries explanation. Mono is the senior face here. Bricolage is the long-form companion.

### Hierarchy

- **Display** *(weight ~600-700, size clamped between roughly 3rem and 5rem, line-height ~0.95-1.05)*: section heroes only. One per landed view. Sized to be the first thing the eye lands on, intentional even when the page is short.
- **Headline** *(weight ~600, size around 1.8-2.2rem, line-height ~1.15)*: section headers. Often paired with a cinnabar rule above.
- **Title** *(weight ~500-600, size around 1.25-1.4rem, line-height ~1.3)*: subsection markers, signal headlines.
- **Body** *(weight ~400, size at minimum 17-18px, line-height ~1.55-1.65)*: the prose. Line length capped at 65 to 75 characters. The body is the product. Treat its rendering as the most important typographic decision.
- **Mono Title** *(weight ~500, size around 0.9-1rem, letter-spacing slightly open)*: the 5-dimension signal profile (e.g. `E3 T-Shifting U2 H-Grounded Z-Now`). Renders inline near the signal title. Always mono. Always identical formatting. Never localized away.
- **Label** *(weight ~600, size around 0.75-0.85rem, uppercase, letter-spacing 0.04-0.06em)*: dates, source domains, category tags. Mono for system metadata, sans-uppercase for editorial labels.

### Named Rules

**The Audit-Trail Rule.** Anything that is part of the source-citation, signal-profile, or evidence chain renders in monospace. The reader can tell at a glance which characters they could right-click and verify.

**The One-Display-Per-View Rule.** Display type appears exactly once on a landed page (the section hero). Repeated display type at the same weight and size is monotony. Subsequent emphasis is a job for headline or pull-quote scale, not another display.

## 4. Elevation

**The system is flat by default.** Surfaces sit on the cream ground without shadow. Depth is conveyed by ink weight, cinnabar emphasis, scale, and rhythm, not by drop-shadows.

The rare exception is the interactive response: a focused or hovered button or link may shift in color, weight, or one to two pixels of vertical translation, never with a soft ambient shadow. Glassmorphism, frosted blur, and decorative elevation are forbidden.

### Named Rules

**The Flat-By-Default Rule.** No element receives a `box-shadow` at rest. Depth at rest is achieved through type weight contrast and tinted neutral layers (Warm Cream as ground, Cream-on-Cream Hairline as a half-step recess), never through shadow.

**The Motion-Echo Rule.** Interactive states (hover, focus, active) may shift color, weight, or 1-2px translation. The transition is exponential ease-out, between 120ms and 220ms. No bounce. No elastic. No layout-property animation.

## 5. Components

*(Components will be authored on the next implementation pass. Day-zero seed: do not document components that do not yet exist. The Component Philosophy below is the constraint kit.)*

**Component Philosophy.** Components in this system feel **engraved**: the type sits on the page like ink sits on paper, with edges that are deliberate but not crisp-clean. Buttons read as confident, not playful. Cards are used only when the affordance is genuinely card-like (a discrete, self-contained unit that lifts from the page); otherwise the surface is unwrapped, with the prose and mono carrying structure. Inputs are stroke-only, no fill, no shadow.

**Hard constraints, in advance of authoring:**

- **No nested cards. Ever.**
- **No same-sized card grids.** If two side-by-side units share the same size, they need to differ in weight, density, or rhythm.
- **No side-stripe borders** (`border-left` or `border-right` greater than 1px as a colored accent). PRODUCT.md and the Impeccable shared design laws both ban this. Use full borders, ground-tint, leading numbers, or nothing.
- **No hero-metric template** (`big number / small label / supporting stats / gradient accent`). The opening of any digest carries argument, not stats theater.
- **Buttons:** sharp 0px corners or near-sharp (2-3px). Never `rounded-full`. Never the SaaS-standard `rounded-lg`. The corner is part of the brand.
- **Inputs:** stroked in deep ink at 1-1.5px, no fill, focus state shifts to cinnabar at the same stroke weight (no glow).
- **Source citations:** mono, full-domain visible (not "(source)"), inline-hyperlinked on first mention, footnote-numbered on subsequent. The citation is not chrome; it is the evidence.

## 6. Do's and Don'ts

### Do

- **Do** anchor every page on warm cream and deep ink, with cinnabar as the single committed accent at 30 to 60 percent of the visible surface.
- **Do** render every signal profile (`E3 T-Shifting U2 H-Grounded Z-Now`) in monospace, identically formatted, with no localization or styling shortcut. The mono is the audit trail.
- **Do** show source URLs in full on first mention. The domain is part of the legibility. "(source)" is not a citation.
- **Do** cap body line length between 65 and 75 characters. Body type sits at 17-18px or higher.
- **Do** use one display-weight headline per landed view. Subsequent emphasis is a job for headline scale, not repeated display.
- **Do** treat whitespace as structure. Generous vertical rhythm between sections; print-grade margin discipline.
- **Do** test all text-on-cinnabar and ink-on-cream combinations at WCAG AA contrast minimum.

### Don't

- **Don't** use purple gradients, navy + gold, or any palette that reads as "MBB corporate slick" or "AI-startup gradient soup." PRODUCT.md names both. They are the bright line.
- **Don't** let the design read as the generic GitHub Pages / MkDocs Material / Just-the-Docs theme. The current site is the anti-reference. The redesign breaks decisively away from sidebar-and-content docs chrome.
- **Don't** use Inter for headlines or as the brand's primary type decision. Inter as system-font fallback is allowed only as a cross-platform safety net.
- **Don't** wrap the body in a content container with a card or shadow. Most surfaces do not need a container.
- **Don't** nest cards inside cards. The pattern is forbidden in this system at every depth.
- **Don't** use `border-left` or `border-right` greater than 1px as a colored stripe on callouts, alerts, or list items. Rewrite the element with a different structure.
- **Don't** use gradient text (`background-clip: text` with a gradient background). Solid color always. Emphasis comes from weight and scale.
- **Don't** rely on color as the sole signal for "strong" versus "weak" or any other categorical distinction. Color is one channel; weight, shape, or label must also carry the meaning.
- **Don't** use bounce or elastic easing. Ease-out exponential curves only. Animation duration between 120ms and 220ms.
- **Don't** add scroll-driven choreography or staggered entrance sequences. Motion is responsive, not performative.
- **Don't** ship a hero-metric template (big number, small label, supporting stats, gradient accent). The opening must carry argument.
- **Don't** use em dashes in any rendered copy. Use commas, colons, semicolons, periods, or parentheses.
