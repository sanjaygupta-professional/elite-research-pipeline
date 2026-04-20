# Monthly Low-Cadence Source Scan — Prompt

You are running a monthly scheduled research scan for the elite-research-pipeline knowledge system. Brand: "Possibilities with Probabilities."

This scan complements the weekly Tier 2 scan (`scripts/weekly-scan-prompt.md`) by covering **low-cadence, high-signal sources** that don't publish weekly — and therefore aren't worth the bloat on the weekly rotation, but still matter quarter-over-quarter.

## Your task

Scan the monthly sources for content published in the **past 30 days**, score any qualifying signals per the framework, and append to the Weak Signal Watch log. You are already in the repo root (`/home/sanjayegupta/projects/elite-research-pipeline`). A branch has already been created for you (`claude/monthly-scan-YYYY-MM-DD`). The wrapper script handles commit and PR creation — you only need to edit files.

## Step 1: Load the framework

Read these two files to understand the scoring rubric:
- `knowledge-system/design/05-signal-scoring-framework.md`
- `knowledge-system/design/06-source-directory.md`

## Step 2: Scan monthly sources

Search the web for content published in the past 30 days from:

**Researcher blogs (infrequent but high-signal):**
- **Andrej Karpathy** — karpathy.ai (cat 01 — posts ~monthly, deep technical)
- **Pranav Mistry / Presight AI** — presight.ai/blog (cat 02/05 Indian enterprise AI)

**Lab blogs (secondary to Anthropic/OpenAI):**
- **Google DeepMind** — deepmind.google/discover (cat 01)
- **Google AI / Gemini** — blog.google/technology/google-deepmind (cat 01)

**Research-feed aggregators:**
- **DAIR AI / Elvis Saravia** — dair.ai (cat 01 paper digests — weekly cadence but overlaps Import AI, so monthly sweep is enough)
- **Underfitted** by Santiago Valderrama — underfitted.io (cat 08/11 practitioner ML)

**Benchmark releases (quarterly at best, but worth catching):**
- **SWE-bench** — swebench.com/blog (cat 01 coding benchmark updates)
- **ARC-AGI / ARC Prize** — arcprize.org (cat 01 reasoning benchmark)

Use WebSearch and WebFetch. If a source has nothing new in the past 30 days, note that and move on.

## Step 3: Classify each article

Apply the Strong / Weak / Noise classification from the framework doc. Discard all Noise immediately. Do not score or log it.

## Step 4: Score qualifying signals

For Strong and Weak signals, score on all 5 dimensions using the compact format:

```
E[1-5] T[Em/Ac/Ma/Sh] U[1-4] H[Gr/Ah/Ph/Poh] Z[Now/Near/Med/Far]
```

## Step 5: Map to category

Assign each signal to one of the 10 knowledge categories (01, 02, 03, 04, 05, 06, 08, 09, 10, 11).

## Step 6: Append to Weak Signal Watch

Append new signals to `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md` under the `## Active Signals Log` section. Use a header that distinguishes this from weekly scans:

```markdown
### Added YYYY-MM-DD (Monthly low-cadence scan)
```

Then use this exact entry format per signal (match existing entries):

```markdown
**[YYYY-MM-DD] | [Signal name]**
**Source:** [Publication, author, article title with URL]
**Profile:** E[n] T-[Type] U[n] H-[Type] Z-[Horizon]
**Category:** [Category number and name]
**Why it matters:** [2-3 sentences explaining implications]
**What to watch for:** [Specific corroboration event]
**Status:** WATCHING
```

## Step 7: Write a scan summary

At the end of your monthly entries, add a dated summary:

```markdown
---
**Monthly Scan Summary — YYYY-MM-DD**
- **Sources scanned:** [list with count of articles reviewed per source]
- **Total articles reviewed:** N
- **Signals added:** N total ([breakdown: strong, weak])
- **Category distribution:** [categories that got new signals]
- **Notable patterns:** [1-2 sentences if cross-source themes emerged]
---
```

## Step 8: If no qualifying signals found

Still add a dated log entry for history continuity:

```markdown
**[YYYY-MM-DD] | Monthly scan — no new signals**
**Sources scanned:** [list]
**Articles reviewed:** N
**Reason:** All content classified as Noise or no fresh posts
```

## Constraints

- **Only modify** `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md`
- Do NOT re-score signals already captured by the weekly scan — check the recent log to avoid duplication
- Do NOT modify baseline research files or other knowledge system documents
- Do NOT commit or push — the wrapper script handles git operations
- Self-verify before finishing: re-read appended entries, check profiles, confirm category mapping, confirm scan summary numbers

When complete, output: "Monthly scan complete. [N] signals added to Weak Signal Watch."
