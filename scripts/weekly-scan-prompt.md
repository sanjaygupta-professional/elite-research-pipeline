# Weekly Tier 2 Source Scan — Prompt

You are running a weekly scheduled research scan for the elite-research-pipeline knowledge system. Brand: "Possibilities with Probabilities."

## Your task

Scan Tier 2 sources for content published in the **past 7 days**, score any signals per the framework, and append qualifying signals to the Weak Signal Watch log. You are already in the repo root (`/home/sanjayegupta/projects/elite-research-pipeline`). A branch has already been created for you (`claude/weekly-scan-YYYY-MM-DD`). The wrapper script will handle commit and PR creation AFTER you finish — you only need to edit files.

## Step 1: Load the framework

Read these two files to understand the scoring rubric:
- `knowledge-system/design/05-signal-scoring-framework.md`
- `knowledge-system/design/06-source-directory.md`

## Step 2: Scan Tier 2 sources

Search the web for content published in the past 7 days from:

**Cross-cutting synthesizers (5):**
- **Import AI** by Jack Clark — importai.substack.com
- **The Batch** by Andrew Ng — deeplearning.ai/the-batch
- **One Useful Thing** by Ethan Mollick — oneusefulthing.org
- **Don't Worry About the Vase** by Zvi Mowshowitz — thezvi.substack.com
- **Stratechery** by Ben Thompson — stratechery.com

**Category specialists (6):**
- **SemiAnalysis** by Dylan Patel — semianalysis.com (cat 05 infra)
- **Simon Willison** — simonwillison.net (cat 08/10 tools + local AI)
- **Latent Space** by Swyx (Shawn Wang) — latent.space (cat 11 agents + AI eng)
- **Interconnects** by Nathan Lambert — interconnects.ai (cat 01 open-source trajectory)
- **Road to AI We Can Trust** by Gary Marcus — garymarcus.substack.com (cat 01/04 contrarian)
- **The Pragmatic Engineer** by Gergely Orosz — newsletter.pragmaticengineer.com (cat 02/08 eng org)

**Workflow & productivity (2):**
- **Every / Chain of Thought** by Dan Shipper — every.to (cat 08/03 AI-in-workflow)
- **Hugging Face blog** — huggingface.co/blog (cat 01/10 open-source model signal)

**First-party lab announcements (2):**
- **Anthropic News** — anthropic.com/news (cat 01/04/08 Claude + policy)
- **OpenAI blog** — openai.com/index (cat 01/08 GPT + product)

**Indian perspective (1):**
- **Analytics India Magazine** — analyticsindiamag.com (Indian AI industry + policy lens)

Use WebSearch and WebFetch. If a source has nothing new in the past 7 days, note that and move on. Total: 16 sources. If total scan time approaches 15 minutes or you're hitting rate limits, prioritize the first 11 and note which were skipped.

## Step 3: Classify each article

Apply the Strong / Weak / Noise classification from the framework doc:

- **STRONG SIGNAL:** multi-source corroboration, real deployment, measurable outcomes
- **WEAK SIGNAL:** one credible source, conceptually sound, directional only
- **NOISE:** vendor hype, echo chamber, no new information

Discard all Noise immediately. Do not score or log it.

## Step 4: Score qualifying signals

For Strong and Weak signals, score on all 5 dimensions using the compact format:

```
E[1-5] T[Em/Ac/Ma/Sh] U[1-4] H[Gr/Ah/Ph/Poh] Z[Now/Near/Med/Far]
```

Where:
- **E** = Evidence Strength (1=theoretical, 5=industry standard)
- **T** = Trajectory (Emerging / Accelerating / Maturing / Shifting)
- **U** = Capability Unlock (1=incremental, 4=paradigm shift)
- **H** = Hype-Reality Gap (Grounded / Ahead / Peak-hype / Post-hype)
- **Z** = Time Horizon (Now / Near / Medium / Far)

## Step 5: Map to category

Assign each signal to the most relevant of the 10 knowledge categories:

- 01 GenAI Capabilities
- 02 Enterprise AI & Org Transformation
- 03 Workforce & Human-AI Collaboration
- 04 AI Governance & Ethics
- 05 AI Infrastructure Trajectory
- 06 Weak Signal Watch (for signals that span multiple categories)
- 08 AI Productivity Tools
- 09 Transformation Methods — AI Era
- 10 Local AI Engineering
- 11 Agent Frameworks & Dev Tools

## Step 6: Append to Weak Signal Watch

Append new signals to `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md` under the `## Active Signals Log` section.

**Use this exact entry format** (match existing entries in the file):

```markdown
**[YYYY-MM-DD] | [Signal name]**
**Source:** [Publication, author, article title with URL]
**Profile:** E[n] T-[Type] U[n] H-[Type] Z-[Horizon]
**Category:** [Category number and name]
**Why it matters:** [2-3 sentences explaining implications]
**What to watch for:** [Specific corroboration event that would upgrade this to a strong signal]
**Status:** WATCHING
```

## Step 7: Write a scan summary

At the end of the Active Signals Log section, add a dated summary entry:

```markdown
---
**Scan Summary — [YYYY-MM-DD]**
- **Sources scanned:** [list with count of articles reviewed per source]
- **Total articles reviewed:** N
- **Signals added:** N total ([breakdown: strong, weak])
- **Category distribution:** [which categories got new signals]
- **Notable patterns:** [1-2 sentences if any cross-source themes emerged]
---
```

## Step 8: If no qualifying signals found

If all content was Noise, still add a dated log entry so the scan history is complete:

```markdown
**[YYYY-MM-DD] | No new signals this week**
**Sources scanned:** [list]
**Articles reviewed:** N
**Reason:** All content classified as Noise or no fresh posts
```

In this case, **skip Step 9** — the dispatch stays on the prior issue.

## Step 9: Update the Cinnabar Dispatch (executive issue)

If you logged at least one qualifying signal in Step 6, update the executive issue at `digest/src/pages/index.astro`. This is the public-facing weekly artifact at `/digest/` and must stay synchronized with each weekly scan.

### Read these first

- `digest/src/pages/index.astro` — the **current** dispatch issue. Use it verbatim as your structural template (component imports, prop shapes, slot patterns, paragraph cadence). Read it carefully before writing.
- `DESIGN.md` — the locked design rules (you only need the "Named Rules" sections; skim, don't memorize).
- `digest/README.md` — summarizes the load-bearing rules. Skim.

### How to write the new issue

Use the `Write` tool to replace `digest/src/pages/index.astro` in full. Start from the prior issue's structure and change only the values listed below. **The `import` block, the `type Strength` / `interface SignalMeta` lines, the audio-path check, and the `<Methodology>` props are stable across issues — copy them verbatim.**

The page uses an **insight-first** structure. Reproduce this exact section order:

1. Frontmatter: the `import` block (copy verbatim), the `issueDate` / `description` / `title` consts, the audio-path check (copy verbatim), and the **`signals` metadata array** (see below).
2. `<Masthead slot="header" ... />` — note `slot="header"`.
3. `<HeroThesis kicker="This week's thesis"> ... </HeroThesis>`
4. `<AudioBrief audioPath={audioPath} issueDate={issueDate} />`
5. `<ClusterCallout kicker="..."> ... </ClusterCallout>` (the insight leads, above the signals)
6. `<SignalIndex signals={signals} />`
7. `<Synthesis>` three `<p>` `</Synthesis>`
8. Five `<Signal {...signals[i]}> ... </Signal>` blocks (i = 0 through 4)
9. `<PreviousIssues currentDate={issueDate} />`
10. `<Methodology slot="footer" ... />` — note `slot="footer"`.

**The `signals` array is the single source of truth.** Author one entry per featured signal (5 of the N). Both `<SignalIndex>` and the `<Signal>` detail blocks read from it, so the metadata is written once. Shape:

```ts
const signals: SignalMeta[] = [
  {
    index: 1,
    date: "YYYY-MM-DD",
    category: "01 GenAI Capabilities · 04 AI Governance & Ethics",
    title: "One declarative sentence. No em-dashes.",
    profile: "E3 T-Ac U3 H-Gr Z-Now",
    strength: "strong",
    sources: [{ label: "domain.com/path", url: "https://domain.com/path" }],
  },
  // ...indexes 2 through 5
];
```
- `label` is the bare domain + path (no `https://` scheme); `url` is the full URL.
- `profile` is the 5-dim string verbatim (e.g. `"E3 T-Ac U3 H-Gr Z-Now"`).
- Selection priorities: Strong over Weak (include 1 Weak only if it materially supports the thesis); cluster-supporting over standalone; cover at least 3 distinct categories across the 5.

**Each `<Signal>` detail block spreads its array entry and supplies prose in slots:**

```astro
<Signal {...signals[0]}>
  <p slot="why">Body prose adapted from "Why it matters" ...</p>
  <p slot="watch">One paragraph adapted from "What to watch for".</p>
</Signal>
```
- `<p slot="why">`: spell out approximate numbers in prose ("eighty-five percent"); preserve digits for exact source figures ("$40K", "82.7%"); `<em>...</em>` once or twice max.
- `<p slot="watch">`: one paragraph.

**The other sections:**

- `<Masthead slot="header">` props: `issueDate`; `scanNumber` = prior issue's value + 1; `signalCount` = total signals from Step 6; `strongCount` + `weakCount` split (must sum to `signalCount`).
- `<HeroThesis>`: 2–4 sentence thesis from the scan's "Notable patterns." A confident editorial claim, not a recap; names the implication for an enterprise AI strategy reader.
- `<AudioBrief>`: pass **both** `audioPath={audioPath}` and `issueDate={issueDate}` (the second drives the on-page transcript, read from your Step 10 script).
- `<ClusterCallout kicker="The pattern across signals X, Y, Z">`: one `<p>` binding 3–4 featured signals to the thesis; one `<strong>...</strong>`.
- `<Synthesis>`: exactly three `<p>`. Para 1 states the pattern (3–5 signals by name). Para 2 the convergence, one `<strong>` max. Para 3 opens `For the reader whose work is enterprise AI strategy:`.
- `<Methodology slot="footer">`: copy props verbatim from the prior issue. Do not edit.

### Voice rules — hard constraints

- **No em-dashes (`—`) anywhere in rendered copy.** Use commas, semicolons, parens, or sentence breaks. This is a top-of-file design rule. Search-and-replace your draft before finishing.
- No hero-metric template (big number + small label).
- Spelled-out numbers in narrative prose; digits in benchmark/dollar figures from sources.
- One `<strong>` in Synthesis para 2, one `<strong>` in ClusterCallout — that is the entire emphasis budget.
- Mono audit trail is handled by the components — do not override styles.

### Self-check before finishing Step 9

- Grep your draft for the `—` character (U+2014). If found, replace with `,` `;` or `(...)`.
- Confirm `scanNumber === priorIssueScanNumber + 1`.
- Confirm `signalCount === strongCount + weakCount` and matches Step 6 totals.
- Confirm the `signals` array has exactly 5 entries with `index` 1 through 5, and every entry's `profile` string appears verbatim in the appended scan section of the weak-signal file.
- Confirm there are exactly 5 `<Signal {...signals[i]}>` blocks, spreads `i = 0` through `4`, each with a `why` and a `watch` slot.
- Confirm the section order matches the list above: Masthead(header) → HeroThesis → AudioBrief → ClusterCallout → SignalIndex → Synthesis → 5 Signals → PreviousIssues → Methodology(footer).
- Confirm `slot="header"` is on `<Masthead>` and `slot="footer"` is on `<Methodology>`.
- Confirm `<AudioBrief>` receives both `audioPath` and `issueDate`.
- Confirm `<PreviousIssues currentDate={issueDate} />` is present. Do NOT reintroduce a raw `import previousIssues from "../data/issues.json"`, a `const filteredIssues = ...`, or an inline `<section class="previous-issues">` block — the `PreviousIssues` component owns all of that now.
- Confirm the `import` block, the `type Strength` / `interface SignalMeta` lines, and the `<Methodology>` props are unchanged from the prior issue.

## Step 10: Write the TTS audio script

If you updated the dispatch in Step 9, also write a 90-second audio brief script for the cloned-voice TTS pipeline. This becomes the cohort's "minimal plus" listening option on the dispatch page.

Write to `digest/audio-scripts/<YYYY-MM-DD>.md` where `<YYYY-MM-DD>` is today's scan date.

### Hard constraints

- **220 to 280 words total.** Aim for 250. Pre-script length budget = ~95 seconds at conversational pace.
- **Open with:** `Sanjay here.` then a one-line hook from the dispatch's HeroThesis. Personal tone, like a voice memo to a peer.
- **Middle:** state the thesis in one or two sentences (rephrased for ear), then 3 to 4 of the strongest signals named with one sentence each, then 1 to 2 sentences from the cluster pattern.
- **Close with:** one-line reader-action (`If your work is enterprise AI strategy, ...`), then `Full detail in the dispatch. Until next week.`

### Voice rules — ear, not eye

- **No em-dashes (—).** Use commas, semicolons, parens.
- **No parentheticals.** TTS pacing on parens is poor; convert to commas.
- **Spell out numbers in narrative prose.** Examples: `eighty-five percent`, `forty thousand to three hundred and twenty thousand dollars`, `twenty twenty-six`. Preserve digits ONLY for benchmark or dollar figures cited verbatim from sources, and only when they read naturally.
- **No URLs spoken aloud.** No `github.io`, no `slash-digest`. The closing CTA "Full detail in the dispatch" suffices.
- **Sentence average length: 15 words.** Long clauses degrade cloned-voice quality. Break sentences on natural pauses.
- **No model identifiers in raw form.** `GPT-5.5` becomes `GPT five point five`. `K2.6` becomes `K two point six`. `ARC-AGI-2` becomes `arc A G I two`. The TTS engine pronounces unaltered model strings poorly.
- **No markdown, no frontmatter, no commentary.** Plain prose paragraphs separated by blank lines. The file is ingested directly into the TTS API.

### Self-check before finishing Step 10

- Word count between 220 and 280.
- Grep for `—` (em-dash) and any URL — both must be absent.
- Confirm "Sanjay here." is the first phrase.
- Confirm "Full detail in the dispatch. Until next week." is the closing.
- Re-read aloud (or simulate it). Any sentence that runs out of breath is too long; split it.

The wrapper script will pass this file through `scripts/gen-audio.sh dispatch` after you finish. If TTS fails (ElevenLabs outage, quota), the dispatch ships without audio (graceful degrade) and the PR notes the failure.

## Constraints

- **You may modify exactly three files:**
  - `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md` (Steps 6–8, always)
  - `digest/src/pages/index.astro` (Step 9, only if at least one signal was added in Step 6)
  - `digest/audio-scripts/<YYYY-MM-DD>.md` (Step 10, only if you updated the dispatch in Step 9)
- Do NOT modify baseline research files, design docs, or any other knowledge system documents.
- Do NOT commit or push — the wrapper script handles git operations after you finish.
- Use self-verification before finishing: re-read your appended entries, verify each profile is formatted correctly per the rubric, confirm the category mapping is correct, confirm the scan summary numbers match the entries added, run the dispatch self-check items in Step 9 if you updated the dispatch, and run the TTS-script self-check items in Step 10 if you wrote the audio script.

When complete, output a brief final message in this exact format:
`Scan complete. N signals added to Weak Signal Watch. Dispatch: updated|skipped. Audio script: written|skipped.`
