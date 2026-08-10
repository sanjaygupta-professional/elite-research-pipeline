# Possibilities with Probabilities

A futures intelligence knowledge system at the intersection of **AI / GenAI** and **Organization Transformation**.

**Live site:** https://cinnabar-intel.github.io/
**Author:** [Sanjay Gupta](https://www.linkedin.com/in/sanjayguptaaccenture/) — Senior Executive, Accenture
**Brand:** Possibilities with Probabilities

---

## What this repo is

Two things in one repo:

1. **Knowledge system** (`knowledge-system/`) — the curated, structured corpus. Strategy, taxonomy, baseline research across 4 zones / 10 categories, rolling weak-signal log, and periodic updates. This is the brain. Published as a [browsable site](https://cinnabar-intel.github.io/) via MkDocs Material.

2. **Pipeline tooling** (`assets/project-template/`, `scripts/`) — automation that scans high-signal sources weekly, scores what it finds, and opens a pull request with new entries for human review before merge. This is the engine.

The methodology, taxonomy, and signal-scoring framework are documented in [`knowledge-system/design/`](knowledge-system/design/).

---

## How the weekly scan works

Every Monday at 6:00 AM IST, a local cron job runs [`scripts/run-weekly-scan.sh`](scripts/run-weekly-scan.sh):

1. Pulls master, creates a fresh branch `claude/weekly-scan-YYYY-MM-DD`
2. Invokes Claude Code in headless mode with the [weekly-scan prompt](scripts/weekly-scan-prompt.md), scanning 16 Tier-2 sources (Import AI, The Batch, SemiAnalysis, Stratechery, Latent Space, Anthropic / OpenAI news, Analytics India Magazine, …)
3. Each candidate is scored on the 5-dimension signal profile defined in [`design/05-signal-scoring-framework.md`](knowledge-system/design/05-signal-scoring-framework.md): Evidence × Trajectory × Uncertainty × Horizon × Z-axis (Now/Near/Med/Far)
4. New signals get appended to `knowledge-system/baseline/zone2-futures-intelligence/06-weak-signal-watch.md` with full sources, profile, why-it-matters, and what-to-watch-for
5. A pull request is opened (never pushes to master directly) — you review, then merge
6. On merge, GitHub Actions ([`.github/workflows/deploy-docs.yml`](.github/workflows/deploy-docs.yml)) rebuilds and redeploys the site within ~1 minute

A monthly low-cadence scan runs on the 1st of each month via [`scripts/run-monthly-scan.sh`](scripts/run-monthly-scan.sh) for slow-moving sources.

Run logs: [`logs/weekly-scans/`](logs/weekly-scans/).

---

## Repo structure

```
elite-research-pipeline/
├── knowledge-system/            ← The brain (published as the live site)
│   ├── design/                  ← Vision, taxonomy, scoring framework, methodology
│   ├── baseline/                ← Comprehensive state across 4 zones / 10 categories
│   │   ├── zone1-present-intelligence/
│   │   ├── zone2-futures-intelligence/
│   │   │   └── 06-weak-signal-watch.md   ← Rolling log; weekly scans append here
│   │   ├── zone3-practitioner-toolkit/
│   │   └── zone4-experimenters-lab/
│   └── updates/                 ← Periodic additions layered on top of baseline
│
├── scripts/                     ← Automation
│   ├── run-weekly-scan.sh           Mondays 6 AM IST
│   ├── run-monthly-scan.sh          1st of month 8:30 AM IST
│   ├── weekly-scan-prompt.md        The prompt the scan runs against
│   ├── viz-pass.py                  Mermaid + PaperBanana injection (baseline files)
│   └── inject_sources.py            Source-citation injection from .sources.yaml sidecars
│
├── assets/project-template/     ← Reusable Python pipeline scaffold (NotebookLM workflow)
├── references/                  ← Architecture notes, API references
├── docs/plans/                  ← Implementation plans (versioned by date)
├── mkdocs.yml                   ← Site config
└── .github/workflows/           ← Deploy pipeline (master → GitHub Pages)
```

---

## Reading the live site

The published site mirrors `knowledge-system/`. Most-visited pages:

- [Vision and positioning](https://cinnabar-intel.github.io/design/01-vision-and-positioning/) — why this system exists
- [Knowledge taxonomy](https://cinnabar-intel.github.io/design/02-knowledge-taxonomy/) — the 4 zones / 10 categories
- [Weak Signal Watch](https://cinnabar-intel.github.io/baseline/zone2-futures-intelligence/06-weak-signal-watch/) — rolling log of newly observed signals (this is where weekly scans land)
- [Signal scoring framework](https://cinnabar-intel.github.io/design/05-signal-scoring-framework/) — how every signal is profiled

Site search is built in (top-right). Visualizations on baseline category files use Mermaid and PaperBanana per [`design/07-visualization-guide.md`](knowledge-system/design/07-visualization-guide.md).

---

## Citation standard

Every substantive source must have an inline hyperlink on first mention plus a `## Sources` section at document end. Workflow: maintain a `<file>.sources.yaml` sidecar, then run `scripts/inject_sources.py`. Full standard in [`design/04-system-methodology.md → Citation Standard`](knowledge-system/design/04-system-methodology.md). Never invent a URL — unverified entries use `url: TODO`.

---

## Local development

```bash
# Knowledge system — preview the site locally
pip install mkdocs-material
mkdocs serve              # http://localhost:8000

# Pipeline tooling
cd assets/project-template
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # add NotebookLM cookies, YouTube API key
python -m pipeline        # run the pipeline
python -m pipeline.cli intel    # inspect generated intel cards
python -m pipeline.cli digest   # generate weekly digest
```
