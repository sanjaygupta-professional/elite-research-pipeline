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

Use the `Write` tool to replace `digest/src/pages/index.astro` in full. Start from the prior issue's structure and change only the values listed below. **The component imports at the top and the `Methodology` props at the bottom are stable across issues — copy them verbatim.**

1. **Frontmatter constants:**
   - `issueDate` = today's scan date (`YYYY-MM-DD`).
   - `description` = one-sentence thesis (used as meta description; under 200 chars).
   - `title` = `"The Cinnabar Dispatch · YYYY-MM-DD · Possibilities with Probabilities"`.

2. **`<Masthead>` props:**
   - `issueDate` — same as above.
   - `scanNumber` — read the prior issue's value (the file you just read) and increment by 1.
   - `signalCount` — total signals you appended in Step 6.
   - `strongCount`, `weakCount` — the strong/weak split (must sum to `signalCount`).

3. **`<HeroThesis kicker="This week's thesis">`:** 2–4 sentence thesis derived from your scan summary's "Notable patterns" section. A confident editorial claim, not a recap. Names the implication for an enterprise AI strategy reader.

4. **`<Synthesis>`:** exactly three `<p>` paragraphs.
   - **Para 1:** State the pattern. Walk through the strongest signals as evidence (mention 3–5 by name/finding).
   - **Para 2:** Convergence/implication. What does the pattern mean structurally? Use one `<strong>...</strong>` for emphasis, max one.
   - **Para 3:** Reader-action paragraph: open with `For the reader whose work is enterprise AI strategy:` and give concrete diligence/playbook implications.

5. **Featured `<Signal>` blocks — select 5 of the N signals.** Selection priorities:
   - Strong over Weak; include 1 Weak only if it materially supports the thesis.
   - Cluster-supporting signals over standalone ones.
   - Cover at least 3 distinct categories across the 5.

   Each `<Signal>` uses these props:
   - `index` — 1 through 5.
   - `date` — signal date in `YYYY-MM-DD`.
   - `category` — e.g. `"01 GenAI Capabilities · 04 AI Governance"` (use middle-dot ` · ` between categories).
   - `title` — one declarative sentence. **No em-dashes.**
   - `profile` — the 5-dim string verbatim (e.g. `"E3 T-Shifting U3 H-Ahead Z-Now"`).
   - `strength` — `"strong"` or `"weak"` exactly.
   - `sources` — array of `{label, url}`. `label` is the bare domain + path (no `https://` scheme); `url` is the full URL.

   Two slots:
   - `<p slot="why">` — body prose adapted from the signal's "Why it matters" entry. Spell out approximate numbers in narrative prose ("eighty-five percent"); preserve digits for exact figures cited from sources ("$40K", "60", "82.7%"). Use `<em>...</em>` once or twice for emphasis, max.
   - `<p slot="watch">` — one paragraph adapted from "What to watch for".

6. **`<ClusterCallout kicker="The pattern across signals X, Y, Z">`:** one `<p>` paragraph binding 3–4 of the featured signals to the thesis. Use `<strong>...</strong>` once for the punch.

7. **`<Methodology>`:** copy props verbatim from the prior issue. Do not edit.

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
- Confirm all 5 featured signal `profile` strings appear verbatim in the appended scan section of the weak-signal file.
- Confirm component imports and `<Methodology>` props are unchanged.

## Constraints

- **You may modify exactly two files:**
  - `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md` (Steps 6–8, always)
  - `digest/src/pages/index.astro` (Step 9, only if at least one signal was added in Step 6)
- Do NOT modify baseline research files, design docs, or any other knowledge system documents.
- Do NOT commit or push — the wrapper script handles git operations after you finish.
- Use self-verification before finishing: re-read your appended entries, verify each profile is formatted correctly per the rubric, confirm the category mapping is correct, confirm the scan summary numbers match the entries added, and run the dispatch self-check items in Step 9 if you updated the dispatch.

When complete, output a brief final message in this exact format:
`Scan complete. N signals added to Weak Signal Watch. Dispatch: updated|skipped.`
