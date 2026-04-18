# Baseline Knowledge — How to Build and Validate

## What the Baseline Is

A comprehensive, point-in-time snapshot of the state of each knowledge category as of **April 2026**. This is the foundation. All periodic updates layer on top — they never replace it.

**Status:** TO BUILD (design complete as of April 2026)

---

## Category File Template

Every category file follows this structure:

```markdown
# [Category Name]
**Zone:** [Zone number and name]
**Last updated:** [Date]
**Baseline status:** [IN PROGRESS / COMPLETE / NEEDS REVIEW]

## State of the Field (as of [Month Year])
[3–5 paragraphs: what is true, what is deployed, what has been proven]

## Key Developments (Past 12 Months)
- [Development 1 — with date and source]
- [Development 2 — with date and source]
- [up to 8 developments]

## The Debate
[Summarize the main tension or disagreement in this field right now.
Who are the optimists and what do they claim?
Who are the skeptics and what do they argue?
What does the evidence support?]

## Sanjay's Current Position
[Not "what the field thinks" — what Sanjay believes, based on the evidence,
informed by his background in transformation/OD. 2–4 sentences.
This will evolve — that evolution is the point.]

## Key Figures / Sources to Track
- [Person or source 1] — [why they matter]
- [Person or source 2] — [why they matter]
- [up to 8 entries]

## Open Questions
- [Question that the field hasn't answered yet — or that Sanjay hasn't resolved]
- [up to 5 questions]

## Connections to Other Categories
- [Category N]: [how they connect]
```

---

## Validation Checklist (Before Marking Any File "COMPLETE")

Run this check against `design/03-success-criteria.md → Component 1`:

- [ ] Coverage: file exists and covers the category substantively (not just headlines)
- [ ] Depth: could brief a knowledgeable peer for 15 minutes from this file alone
- [ ] Recency: past 12 months of significant developments are present
- [ ] Perspective balance: at least one optimist, one skeptic, one practitioner voice
- [ ] POV readiness: can write 2–3 "I believe..." statements from memory after reading
- [ ] **Citations: every substantive source has an inline hyperlink (first mention) and a footnote marker (subsequent mentions), plus an entry in the `## Sources` section** — see `design/04-system-methodology.md → Citation Standard`

---

## Source Citation Workflow (Non-Negotiable)

Every category file MUST carry verified URLs for every substantive source it cites. Named-only mentions ("McKinsey State of AI 2025" without a link) are not acceptable.

### How it works

1. Each `<file>.md` has a sidecar `<file>.sources.yaml` listing every substantive source (papers, reports, benchmarks, articles, newsletters, people in Sources to Track).
2. Run `python3 scripts/inject_sources.py <file>.md` — it rewrites the markdown with:
   - First mention of each source → full inline hyperlink `[anchor](url)`
   - Subsequent mentions → footnote marker `[^key]`
   - A `## Sources` section at the bottom (grouped by type)
3. The sidecar YAML is the source-of-truth. Edit it to fix URLs; re-run the injector.

### Sidecar schema

```yaml
- key: peng-2023
  type: paper              # paper | report | benchmark | article | newsletter | person | organization
  authors: Peng, Kalliamvakou, et al.
  title: "The Impact of AI on Developer Productivity: Evidence from GitHub Copilot"
  venue: arXiv:2302.06590
  year: 2023
  url: https://arxiv.org/abs/2302.06590
  first_mention_anchor: "Peng et al. (GitHub, 2023, now widely replicated)"  # exact prose substring
  all_mentions:
    - "Peng et al."        # shorter phrasings used later in the doc
```

Full schema documented in `scripts/inject_sources.py`. The injector is idempotent — running it twice produces no diff.

### Adding / updating a source

- Editing prose that adds a new source mention? Add the entry to the sidecar YAML, then re-run the injector.
- URL broke / paper moved? Edit the YAML, re-run the injector.
- Never edit inline links or footnote definitions by hand — the YAML will overwrite them.

---

## Build Order (Recommended)

Start with the categories most central to Sanjay's current work and DBA research, then fill outward:

1. GenAI Capabilities (Zone 1) — foundational to everything
2. Enterprise AI & Org Transformation (Zone 1) — core differentiator
3. AI Infrastructure Trajectory (Zone 2) — feeds futures POV
4. AI Productivity Tools (Zone 3) — immediate practitioner credibility
5. Workforce & Human-AI Collaboration (Zone 1)
6. Agent Frameworks & Dev Tools (Zone 4)
7. Transformation Methods — AI Era (Zone 3)
8. AI Governance & Ethics (Zone 1)
9. Local AI Engineering (Zone 4)
10. Weak Signal Watch (Zone 2) — ongoing, never "complete"
11. Long-Arc Futures POV (Zone 2) — synthesized last, from all others

---

## Folder Structure

```
baseline/
├── README.md                              ← This file
├── zone1-present-intelligence/
│   ├── 01-genai-capabilities.md
│   ├── 02-enterprise-ai-org-transformation.md
│   ├── 03-workforce-human-ai-collaboration.md
│   └── 04-ai-governance-ethics.md
├── zone2-futures-intelligence/
│   ├── 05-ai-infrastructure-trajectory.md
│   ├── 06-weak-signal-watch.md
│   └── 07-long-arc-futures-pov.md
├── zone3-practitioner-toolkit/
│   ├── 08-ai-productivity-tools.md
│   └── 09-transformation-methods-ai-era.md
└── zone4-experimenters-lab/
    ├── 10-local-ai-engineering.md
    └── 11-agent-frameworks-dev-tools.md
```
