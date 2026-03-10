# Google Workspace Integration — Design Document

## Goal

Integrate Google Workspace CLI (`gws`) into the Futures Intelligence System as a durable cloud storage backend and semi-automatic distribution channel, leveraging 2TB Google Workspace storage.

## Architecture

One new module (`pipeline/workspace.py`) wraps the `gws` CLI via subprocess. Auto-syncs artifacts and intel cards to Google Drive on every pipeline run. Distribution (sharing, emailing) is triggered manually via CLI commands. Pipeline never fails due to workspace sync errors.

## Tech Stack

- `gws` CLI (npm: `@googleworkspace/cli`) — subprocess calls, JSON output
- Google Drive, Docs, Sheets, Gmail — via `gws` commands
- No Google API client library — zero Python dependency

---

## Drive Folder Structure

```
My Drive/
└── Futures Intelligence/
    ├── Index (Google Sheet — master tracker)
    ├── Intel Cards/
    │   ├── 2026-03/
    │   │   ├── AI Agents Reshape Enterprise Workflows.gdoc
    │   │   └── Foundation Models Hit Reasoning Ceiling.gdoc
    │   └── 2026-04/
    ├── Artifacts/
    │   ├── 2026-03/
    │   │   ├── ai-agents-enterprise/
    │   │   │   ├── slides.pdf
    │   │   │   ├── slides_storytelling.pdf
    │   │   │   └── audio_overview.mp3
    │   │   └── foundation-models-ceiling/
    │   └── 2026-04/
    ├── Digests/
    │   ├── Week of March 09, 2026.gdoc
    │   └── Week of March 16, 2026.gdoc
    └── Drafts/
        ├── LinkedIn/
        └── X/
```

**Scalability:**
- Monthly subfolders cap browsing depth (~30 items max per folder)
- Append-only Index Sheet (10M cell limit = ~50 years at 10 items/day)
- After 6 months, old rows archive to an "Archive" sheet tab

---

## Index Sheet Design

### Sheet 1: Items

| Date | Title | Source | Score | Themes | Status | Intel Card | Artifacts | URL |
|------|-------|--------|-------|--------|--------|------------|-----------|-----|
| 2026-03-10 | AI Agents Reshape... | YouTube | 8 | AI Agents, Enterprise | done | [link] | [slides] [audio] | [source] |

- Every cell with a reference is a clickable hyperlink
- Frozen header row + saved filter views ("This Week", "High Score Only", "By Theme")
- All values written by pipeline — no formulas, zero fragility

### Sheet 2: Themes

| Theme | Count (30d) | Trend | Top Possibility |
|-------|-------------|-------|-----------------|
| AI Agents | 12 | up | Enterprise workflows fully autonomous |

- Pre-computed in Python, written directly — not Sheet formulas

---

## Navigation: 3-Click Rule

From anywhere, reach any item in 3 clicks or less.

**Entry points:**
1. **By time** — Index Sheet → filter by date → click link
2. **By theme** — Themes tab → click theme → filtered view
3. **By search** — Google Drive search (intel cards are Google Docs = full-text indexed)
4. **By digest** — Digests folder → inline links to referenced cards

**Every Intel Card doc links back to Index. Every Index row links to its doc.**

---

## Writing Style: Hemingway-Kelly-Godin + Socratic Synthesis

### Core Voice

**From Hemingway:** Short sentences. Active voice. No adjective bloat. If a sentence works without a word, remove the word.

**From Kevin Kelly:** Optimistic futurism. Name the possibility, not the fear. Frame technology as expanding what humans can do. Think in decades, write about now.

**From Seth Godin:** Lead with the provocative question. Short paragraphs — often one sentence. End with the implication, not the conclusion.

### Socratic Self-Dialogue Layer

Questions under 10 words. Answers under 25 words. At least one self-challenge per piece ("But wait", "So what", "Really?"). End with a forward-looking question, not a closed answer.

**Example:**

> GPT-5 passes the bar exam at the 98th percentile.
>
> So what? AI has been passing exams for years.
>
> Yes. But passing isn't the point. Cost is the point. This exam attempt cost $0.12.
>
> What happens when legal reasoning costs $0.12?
>
> Every small business gets a lawyer. Every contract gets reviewed. Every dispute gets analyzed before it escalates.
>
> But wait — does cheap legal reasoning mean better justice?
>
> Not automatically. Cheap reasoning without human judgment is just fast mistakes. The winners pair AI speed with human stakes-awareness.
>
> Probability: High. Timeframe: 12 months.
>
> The question isn't whether this happens. It's whether your industry is ready when it does.

### Style Rules

- Sentences under 15 words where possible
- One idea per paragraph
- Questions before answers
- Concrete over abstract ("one lawyer replacing ten" not "increased productivity")
- End with forward momentum — what to watch, what to do

---

## Intel Card Google Doc Template

**Title:** `[Title] — Futures Intelligence Card`

```
━━━ Futures Intelligence Card ━━━
Source: [clickable URL]
Score: 7 | Themes: AI Agents, Enterprise AI
Date: 2026-03-10
Artifacts: slides | slides_storytelling | audio
Index: <- Back to Master Index
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SIGNALS
- [signal 1]
- [signal 2]

POSSIBILITIES WITH PROBABILITIES

What if [scenario 1]?

[Socratic self-dialogue — 2-3 Q&A exchanges, ending with implication]

Probability: High | Timeframe: 6-12 months

What if [scenario 2]?

[Same pattern]

Probability: Medium | Timeframe: 12-24 months

IMPLICATIONS
- [who is affected and how]

WHAT TO DO
- [actionable advisory — Hemingway direct]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#PossibilitiesWithProbabilities
```

---

## Weekly Digest Doc Template

**Title:** `Futures Intelligence Digest — Week of [date]`

```
━━━ Futures Intelligence Digest ━━━
Week of March 10, 2026
Items processed: 23 | Intel cards: 18 | Skipped: 5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THIS WEEK'S SIGNAL

[Single most important signal. One paragraph. Why it matters now.]

THEMES IN MOTION

AI Agents (7 signals)
The pattern is clear. [2-3 sentences synthesizing collective meaning.]
-> Cards: [link] [link] [link]

Enterprise AI (4 signals)
[Same pattern]
-> Cards: [link] [link]

POSSIBILITIES TO WATCH

1. [Highest-probability possibility]
   Probability: High | Timeframe: 6 months
   Why now? [One sentence]

2. [Second possibility]
   Probability: Medium | Timeframe: 12 months

3. [Third]

WHAT TO DO THIS WEEK

- [Most actionable advisory, synthesized across cards]
- [Second]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#PossibilitiesWithProbabilities
```

---

## Module Design: `pipeline/workspace.py`

```
workspace.py
├── WorkspaceSync (class)
│   ├── ensure_folder_structure()  — create monthly folders if missing
│   ├── upload_artifacts()         — upload PDF/MP3 to Drive
│   ├── create_intel_card_doc()    — create Google Doc from intel card dict
│   ├── update_index_sheet()       — append row with hyperlinks
│   ├── update_themes_sheet()      — refresh theme counts
│   └── create_digest_doc()        — create weekly digest as Google Doc
│
├── _run_gws()  — subprocess wrapper for gws CLI
│   ├── Parses JSON output
│   ├── Handles auth errors gracefully
│   └── Returns None on failure (never crashes pipeline)
│
└── Style helpers
    ├── format_intel_card_body()   — applies Socratic style to card dict
    └── format_digest_body()       — applies synthesis style to weekly cards
```

---

## Pipeline Integration

### Automatic (every run)

In `artifacts.py`, after intel card extraction:

```python
# Auto-sync to Google Workspace (non-blocking, failure-tolerant)
if config.workspace.enabled:
    await workspace_sync(item, intel_card, succeeded_artifacts)
```

### On-Demand (CLI commands)

```bash
# Publishing
python -m pipeline.cli publish digest          # Create digest as Google Doc
python -m pipeline.cli publish draft linkedin   # Create LinkedIn draft in Drafts/

# Sharing
python -m pipeline.cli share digest --email team@company.com
python -m pipeline.cli share folder --with colleague@gmail.com
```

---

## Config Addition

```yaml
workspace:
  enabled: false                              # opt-in
  root_folder: "Futures Intelligence"
  index_sheet_name: "Futures Intelligence Index"
  auto_sync: true                             # upload artifacts + create docs each run
```

---

## Failure Handling

- Workspace sync failures are logged as warnings, never errors
- Pipeline always completes local processing first
- If `gws` auth expires: log "please run `gws auth login`", skip sync, retry next run
- If Drive is unreachable: skip sync, local artifacts are still complete

---

## Automation Level

| Action | Trigger | Notes |
|--------|---------|-------|
| Upload artifacts to Drive | Automatic (each run) | PDF, MP3 to monthly folders |
| Create Intel Card Google Doc | Automatic (each run) | With nav header + Socratic style |
| Update Index Sheet | Automatic (each run) | Append row with hyperlinks |
| Update Themes Sheet | Automatic (each run) | Refresh counts |
| Create weekly digest doc | Manual (`cli publish digest`) | In Digests/ folder |
| Create LinkedIn/X draft | Manual (`cli publish draft`) | In Drafts/ folder |
| Share folder with collaborator | Manual (`cli share folder`) | Via Drive sharing |
| Email digest | Manual (`cli share digest`) | Via Gmail |

---

## Dependencies

- `gws` CLI installed separately (`npm install -g @googleworkspace/cli`)
- No new Python package dependencies
- `gws auth login` for initial OAuth setup (one-time)
