---
name: elite-research-pipeline
description: Automated content consumption pipeline that processes YouTube playlists and URLs through Google NotebookLM to generate synthesized artifacts (audio overviews, slide decks, infographics). Use when the user wants to (1) set up an automated research pipeline from YouTube to NotebookLM, (2) process a YouTube URL or playlist into audio overviews, slides, or infographics, (3) scaffold a project that integrates notebooklm-py with YouTube Data API v3, or (4) configure artifact generation styles and prompt templates for NotebookLM.
---

# Elite Research Pipeline

Automate your content consumption pipeline: YouTube playlists → NotebookLM → synthesized artifacts (audio overviews, slides, mind maps).

## What It Does

You add videos to a custom YouTube "Research Queue" playlist (or pass a single URL). The pipeline:
1. **Collects** new items from the playlist via YouTube Data API v3 (or accepts a single URL)
2. **Deduplicates** against a local SQLite database
3. **Creates one NotebookLM notebook per item** — all artifacts live inside this single notebook
4. **Generates all artifacts in parallel** within the notebook (dual slide decks, audio, 9 infographic variants)
5. **Tracks status** in SQLite (new/processing/done/failed) with retry support

Each run is idempotent — already-processed items are skipped. Zero Claude tokens used at runtime — all generation happens via Google's NotebookLM API.

## Quick Start

### 1. Set Up the Project
```bash
cd <your-project-directory>

# Copy the project template
cp -r <skill-path>/assets/project-template/* .
cp <skill-path>/assets/project-template/.env.example .
cp <skill-path>/assets/project-template/.gitignore .

# Run setup (installs deps, guides through auth)
bash scripts/setup.sh
```

### 2. Configure
1. Create a "Research Queue" playlist on YouTube
2. Edit `config.yaml` — set your `playlist_id`
3. Edit `.env` — add YouTube OAuth credentials
4. Add 1-2 test videos to the playlist

### 3. Run
```bash
# Full playlist run
python -m pipeline.main

# Single URL
python -m pipeline.single_url "https://www.youtube.com/watch?v=abc123"
python -m pipeline.single_url "https://youtu.be/abc123" --title "Custom Title"
```

## Configuration

### config.yaml
```yaml
pipeline:
  max_items_per_run: 5       # Rate limit protection
  artifacts_dir: "./artifacts"
  db_path: "./pipeline.db"
  dual_slides: true          # Two slide decks: playbook + auto-selected contextual style
  infographics: true         # All 9 infographic variants (3 orientations x 3 detail levels)

artifact_types:               # What to generate per item
  - slides                    # Slide deck (japanese_minimal playbook by default)
  - audio_overview            # Deep-dive audio discussion

styles:
  slides: "japanese_minimal"  # japanese_minimal, executive, minimal, technical, storytelling, visual, educational
  audio: "deep_dive"          # deep_dive, brief, critical

sources:
  youtube:
    enabled: true
    playlist_id: "PLxxxxxx"   # Your playlist ID
```

### Artifact Types
| Type | Output | Description |
|------|--------|-------------|
| `audio_overview` | `.mp3` | Audio discussion of the content |
| `slides` | `.pdf` | Slide deck summarizing key points |
| `mind_map` | `.json` | Structured mind map |
| `infographic` | `.png` | Visual infographic |

### Prompt Styles
The pipeline uses curated prompt templates for high-quality artifact generation.
Set styles in `config.yaml`:

```yaml
styles:
  slides: "executive"    # executive, minimal, technical, storytelling, visual, educational
  audio: "deep_dive"     # deep_dive, brief, critical
```

See `references/slide-prompts.md` for full details and customization guide.
Prompts inspired by [awesome-notebookLM-prompts](https://github.com/serenakeyitan/awesome-notebookLM-prompts).

## Architecture

See `references/architecture.md` for full details.

```
YouTube Playlist → youtube.py → SourceItem → processor.py → db.py
    → notebooklm.py → artifacts.py → artifacts/{date}/{slug}/
```

## Troubleshooting

### NotebookLM auth expired
```
ERROR: NotebookLM authentication error. Please run: notebooklm login
```
Run `notebooklm login` — session cookies expire every few weeks.

### YouTube OAuth
First run opens a browser for Google OAuth. Token saves to `youtube_token.json`.
If token expires, delete the file and re-run.

### Rate limits
Default `max_items_per_run: 5` with built-in delays. Reduce if hitting limits.

## References
- `references/notebooklm-api.md` — notebooklm-py API methods and gotchas
- `references/youtube-api.md` — YouTube Data API patterns and OAuth setup
- `references/architecture.md` — Full architecture and data flow
