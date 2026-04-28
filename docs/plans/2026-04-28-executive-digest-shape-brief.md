# Shape Brief: Executive Digest Page

**Target:** `executive-digest-page` (the weekly editorial dispatch surface)
**Status:** Pending user confirmation. Complete when explicitly approved.
**Authored:** 2026-04-28

---

## 1. Feature Summary

A weekly editorial dispatch (the "Cinnabar Dispatch") that turns each completed Tier 2 source scan into a designed argument: a thesis at the top, a brief synthesis, and 3 to 5 of the week's strongest signals as evidence. Each issue gets a stable URL and is indexed in a chronological archive at `/digest/`. The first published issue is **2026-04-27**, sourced from PR #4's seven signals.

The digest is the brand's primary outward-facing surface. The MkDocs documentation site continues to serve as the deep archive; the digest is what lands when someone follows a LinkedIn link.

## 2. Primary User Action

**Read the thesis. Trust it because the evidence is right there.** The reader is a transformation leader or consulting peer between meetings. They opened the link from a LinkedIn DM or calendar reminder. The single thing they need to leave with is a sharp, defensible take that they can use in their next client conversation. Everything else (sources, profiles, methodology) is auditable but secondary.

## 3. Design Direction

- **Register:** brand (per `PRODUCT.md`).
- **Color strategy:** Committed (per `DESIGN.md`). Warm cream as ground (`oklch(96% 0.01 85)` target), deep ink as type (`oklch(15% 0.02 60)`), cinnabar (`oklch(58% 0.18 35)`) as the single committed accent at 30 to 60 percent of surface in deliberate roles (issue rule, signal-strength chips, footnote markers, accent quotes, the methodology callout).
- **Scene sentence:** *A transformation leader, between two meetings, opens a LinkedIn DM on a 14-inch laptop in conference-room daylight, with thirty seconds of attention before the next call. They will either leave with a sharper take or close the tab.* The daylight + brief-attention scene forces light theme, generous type, no decorative chrome.
- **Anchor references** (from `DESIGN.md`): The Generalist (thesis-driven essay framing), a16z Future (manifesto-bold opening, willingness to stake a position), Stripe Press (research-grade typographic craft, restraint with weight contrast).
- **Anti-references** (from `PRODUCT.md` and the additional one named in `DESIGN.md` setup): MBB corporate slick, AI-startup gradient soup, generic GitHub Pages docs theme. The current MkDocs Material site is the docs-aesthetic anti-reference; the digest must read as *not* coming from the same surface.

## 4. Scope

- **Fidelity:** production-ready.
- **Breadth (this build):** the **2026-04-27 issue page** with real content from the merged scan. Archive index at `/digest/` is a separate near-term build (small, but not in this brief).
- **Interactivity:** static. No JS-driven filtering, no live search, no dynamic data. Source links are real anchor tags. Hover and focus states only.
- **Time intent:** ships. This issue replaces the current MkDocs Weak Signal Watch page as the canonical reading surface for this week's scan.

## 5. Layout Strategy

The page is **a single vertical column** with deliberate rhythm shifts, not a grid of cards. Layout follows the editorial dispatch reference set, not a docs-site sidebar layout. Body width caps at roughly 720px (65 to 75ch at the chosen body size). The page reads top to bottom and is meant to be read.

**Vertical sections, in order:**

1. **Issue masthead** (thin, top-aligned, mono): publication name, week-of date, scan number, signal counts. Reads like a journal masthead, set in mono. No logo.
2. **Hero thesis** (display sans, large, cinnabar rule above): one or two sentences that stake the position. Set generous, with breathing room equal to or greater than its own height. The cinnabar rule is the only chromatic element above the thesis.
3. **Synthesis paragraphs** (body sans, 2 to 4 paragraphs): the argument in prose. First-person, confident. Inline cinnabar emphasis where structurally meaningful, never decoratively. Footnote markers in cinnabar lead to the Sources section.
4. **Selected signals section** (label + headline + body per signal, 3 to 5 entries): each signal renders as a typographic block, not a card. Title in headline weight, monospaced 5-dimension profile inline below the title (`E3 T-Shifting U2 H-Grounded Z-Now`), category label in mono uppercase, source citations inline-hyperlinked with full domain visible. Body paragraph(s). "What to watch for" callout in a cinnabar-rule-flanked block. Vertical separator between signals is a thin Cream-on-Cream Hairline, not a card border.
5. **Cluster-pattern callout** (if applicable): a one-paragraph block that names the cross-signal pattern surfaced by the scan. Set apart from individual signals through scale and rule treatment, not through a different color.
6. **Methodology footer** (mono, smaller scale): a one-line statement of how signals are scored (5-dimension profile defined), with a hyperlink to the full framework on the MkDocs site. Compact, no decoration.
7. **Sources** (numbered list, body sans): every footnote target with full URL visible. Mirrors the existing citation standard.

**Rhythm:** vertical spacing is **not uniform**. The space above the hero thesis is the largest gap on the page. Space between signals is moderate. Space inside a signal block (between title, profile, body, callout) is tight. Whitespace is structure, not absence.

**Asymmetric move:** the cinnabar rule above the hero thesis is left-aligned at a fixed measure (e.g., 80px wide), not full width. This is the page's signature visual asymmetry and the brand's typographic anchor.

## 6. Key States

- **Default (the live issue):** rendered with the 2026-04-27 content. This is the only state for the production-ready scope of this brief.
- **Empty (issue not yet published):** out of scope for the issue page itself (each issue has its own URL and is published only when content exists). For the future archive index, an empty state is "No issues yet. The first scan runs Mondays, 6 AM IST."
- **Error (404 on a malformed `/digest/<date>/` URL):** out of scope for this build. Default GitHub Pages 404 acceptable until archive ships.
- **No-cluster-pattern week:** if a future scan does not surface a cluster pattern, the cluster-pattern callout (section 5.5 above) is omitted entirely. Page still works; layout absorbs the missing block without an empty placeholder.
- **Reduced-motion preference:** all transitions disabled. Hover states fall back to color and weight changes only, no translation. Per `DESIGN.md` and PRODUCT.md a11y rules.

## 7. Interaction Model

- **Source links** in inline citations and the Sources section open in the same tab (the reader is mid-read, not exploring; honor that).
- **Hover states** on links: cinnabar-to-deep-ink color shift on text links, transition between 120ms and 220ms, exponential ease-out. Underline appears on hover, not at rest, to keep the prose visually quiet.
- **Hover states** on the methodology footer link: same treatment; the footer stays demure.
- **Focus states** (keyboard): cinnabar focus ring, 2px stroke, no glow. Per `DESIGN.md` (`The Motion-Echo Rule`).
- **Scroll:** static. No scroll-driven entrance choreography (per `DESIGN.md` motion = responsive, not choreographed). The page does not perform.
- **No modals, no overlays, no popovers.** Footnote markers jump to the Sources section anchor.

## 8. Content Requirements

**For the 2026-04-27 issue (real content from the merged PR #4):**

- **Issue masthead:** "POSSIBILITIES WITH PROBABILITIES · WEEKLY DISPATCH · 2026-04-27 · SCAN #3 · 7 SIGNALS · 5 STRONG · 2 WEAK"
- **Hero thesis:** drawn directly from the cluster-pattern callout in the scan run log: *"The infrastructure layer is now the binding constraint for 2026 enterprise AI. Three of this week's seven signals say so, and they sharpen the prior week's compute-supply inflection from observation into structural pattern."*
- **Synthesis (2 to 4 paragraphs):** authored from the existing run log + selected signal bodies. Should explicitly name the three corroborating signals and why their convergence matters.
- **Selected signals (3 strong, 2 supporting):** the three cluster-pattern signals plus two strong supplementary signals.
   1. Anthropic-Amazon 5 GW expansion (Cat 05 Infrastructure)
   2. DeepSeek V4 1M-context with ~2% KV cache (Cat 01 Capabilities, Cat 11 Agent Frameworks)
   3. US data-center community revolt (Cat 05 Infrastructure, Cat 04 Governance)
   4. Cost-per-task overtaking $/token (Cat 08 Productivity, Cat 02 Enterprise)
   5. Indian IT enterprise-AI revenue inflection (Cat 02 Enterprise)
- **Each signal block** carries: date, title, source citation (with full URL), 5-dimension profile in mono, category mapping, "Why it matters" body, "What to watch for" callout. All directly from the existing weak-signal-watch.md entry; the design surfaces it editorially without rewriting.
- **Cluster-pattern callout:** the cross-signal observation about infrastructure-as-binding-constraint, lifted from the run log.
- **Methodology footer:** "Signals are scored on a 5-dimension profile (Evidence, Trajectory, Uncertainty, Horizon, Z-axis). Full framework: [link to design/05-signal-scoring-framework.md on the MkDocs site]."
- **Sources:** numbered list of every URL referenced, full domain visible, in body sans.

**Realistic content ranges (for future issues):**

- Signals per scan: 5 to 9 typical (this week is 7).
- Selected for digest: 3 to 5.
- Hero thesis length: 1 to 2 sentences, max ~280 characters.
- Synthesis length: 2 to 4 paragraphs.
- Sources per issue: 15 to 30 unique URLs.

**Copy constraints:**

- No em-dashes in any rendered copy. Per `DESIGN.md`.
- First-person, confident voice. No "we believe" hedging. Per `PRODUCT.md` brand personality.
- Sources visible by full domain on first mention, not "(source)".

## 9. Recommended References (for the craft pass)

- **typography.md**: the Display + mono pairing is the brand's primary typographic move; font selection per `brand.md`'s reflex-reject list and selection procedure must run during craft.
- **color-and-contrast.md**: verifying the cinnabar / cream / ink palette at WCAG AA on every text-on-color combination, with target OKLCH values resolved to actual hex once chosen.
- **spatial-design.md**: the asymmetric cinnabar rule, the rhythm shifts between sections, the 65-75ch body cap, the section-spacing variance.
- **interaction-design.md**: the hover + focus state design across links, footnote markers, and source citations.
- **responsive-design.md**: single-column scales naturally, but the masthead, hero asymmetry, and signal blocks need explicit mobile handling.
- **ux-writing.md**: the editorial voice carries the brand; the masthead labels, methodology line, and footer copy all need passes.

## 10. Open Questions

These are deliberately deferred to the craft pass; the brief is approvable without resolving them.

1. **Font family choice (display sans + mono).** `DESIGN.md` directional candidates: Söhne, GT America, Neue Haas Grotesk for display; Berkeley Mono, JetBrains Mono, Commit Mono for monospace. License costs and self-host decisions resolve at craft time. Open Sans / Inter explicitly excluded.
2. **Astro project location in the repo.** Two options: a `digest/` directory at the repo root with its own `package.json`, or absorbed under `assets/project-template/`. Recommend the former for clean separation.
3. **Content sourcing.** Two options: (a) author each issue as a markdown file under `digest/issues/2026-04-27.md` and have Astro render it, or (b) parse `06-weak-signal-watch.md` directly and select signals algorithmically. Recommend (a) for control; the digest is editorial, not a dump.
4. **Archive index page.** Out of scope here; flag a separate shape pass after the issue page ships.
5. **The exact thesis sentence for the 2026-04-27 issue.** Drafted above from the run log; the user may want to revise the wording before the craft pass commits it to the page.

---

## Confirmation gate

Per the shape skill, this brief is incomplete until the user explicitly confirms. The next reasonable action after confirmation is `/impeccable craft executive-digest-page` (which will re-run shape internally for safety, then build).
