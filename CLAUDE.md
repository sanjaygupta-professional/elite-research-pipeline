# CLAUDE.md — Elite Research Pipeline / Futures Intelligence System

## What This Project Is

A personal **knowledge system + automated research pipeline** for Sanjay Gupta, Senior Executive at Accenture. Two layers:

1. **Knowledge System** (`knowledge-system/`) — the strategy, taxonomy, baseline research, and ongoing intelligence. This is the *brain*. Start here for context.
2. **Pipeline Tooling** (`assets/project-template/`) — Python async pipeline that automates source collection → NotebookLM processing → Intel Card generation → Publishing. This is the *engine*.

## Purpose

Build and maintain thought leadership at the intersection of **AI/GenAI** and **Organization Transformation** under the brand **"Possibilities with Probabilities"**.

## Where to Start

- **Understanding the system:** `knowledge-system/README.md`
- **Strategy & design decisions:** `knowledge-system/design/`
- **Baseline research (what we know up to today):** `knowledge-system/baseline/`
- **Ongoing updates (periodic additions):** `knowledge-system/updates/`
- **Pipeline implementation plan:** `docs/plans/2026-03-10-futures-intelligence-system.md`
- **Pipeline architecture:** `references/architecture.md`

## Key Decisions Already Made

- Knowledge taxonomy: 4 zones, 10 categories (see `knowledge-system/design/02-knowledge-taxonomy.md`)
- Brand: "Possibilities with Probabilities"
- Methodology: success criteria defined BEFORE planning or implementation
- Baseline first, then periodic updates layered on top
- Signal classification: Strong / Weak / Noise across all categories

## Commands (Pipeline)

All pipeline commands run from `assets/project-template/`:
```bash
cd assets/project-template
source venv/bin/activate          # Python 3.12 venv
python -m pipeline                # Run pipeline
python -m pipeline.cli intel      # Show intel cards
python -m pipeline.cli themes     # Show trending themes
python -m pipeline.cli digest     # Generate weekly digest
```

## What NOT to Do

- Do not edit files in `assets/project-template/pipeline/__pycache__/`
- Do not fill baseline category files with invented/hallucinated content — baseline research must come from real sources
- Do not skip the success criteria validation step before declaring any component "done"
- **Do not publish any research (baseline, updates, intel cards, digests, LinkedIn/X drafts) without sources.** Every substantive source must have (a) a full inline hyperlink on first mention and (b) a footnote marker on subsequent mentions, plus a `## Sources` section at the document end. Workflow: `<file>.sources.yaml` sidecar → `scripts/inject_sources.py`. Full standard: `knowledge-system/design/04-system-methodology.md → Citation Standard`. Never invent a URL — if unverified, use `url: TODO`.
