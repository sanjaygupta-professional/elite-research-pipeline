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

- **Import AI** by Jack Clark — importai.substack.com
- **The Batch** by Andrew Ng — deeplearning.ai/the-batch
- **One Useful Thing** by Ethan Mollick — oneusefulthing.org
- **Don't Worry About the Vase** by Zvi Mowshowitz — thezvi.substack.com
- **Stratechery** by Ben Thompson — stratechery.com

Use WebSearch and WebFetch. If a source has nothing new in the past 7 days, note that and move on.

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

## Step 6b: Regenerate Signal Landscape Quadrant for updated categories

For each baseline category file that received new signals in Step 6, regenerate its Signal Landscape Quadrant diagram. This is the only diagram type updated by the weekly scan — do NOT touch any other diagrams.

**Run the viz-pass script in update-quadrant-only mode:**
```bash
python scripts/viz-pass.py <path-to-category-file> --update-quadrant-only
```

The script will:
1. Re-parse all signal profiles (E, Z dimensions) from the Signal Assessment section
2. Replace the existing `quadrantChart` mermaid block with an updated one
3. Print confirmation

If the script is not available, manually update the `quadrantChart` mermaid block in the Signal Assessment section using this template from `knowledge-system/design/07-visualization-guide.md`:
- X-axis: Evidence (E1=0.1, E2=0.3, E3=0.5, E4=0.75, E5=0.9)
- Y-axis: Time Horizon (Now=0.1, Near=0.35, Med=0.65, Far=0.9)

**Note:** The `06-weak-signal-watch.md` file does not have a quadrant chart. Only update quadrant charts in the specific baseline category files where signals were categorized.

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

## Constraints

- **Only modify** `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md`
- Do NOT modify baseline research files or any other knowledge system documents
- Do NOT commit or push — the wrapper script handles git operations after you finish
- Use self-verification before finishing: re-read your appended entries, verify each profile is formatted correctly per the rubric, confirm the category mapping is correct, confirm the scan summary numbers match the entries added

When complete, output a brief final message: "Scan complete. [N] signals added to Weak Signal Watch."
