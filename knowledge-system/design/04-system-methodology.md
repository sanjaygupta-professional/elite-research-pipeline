# System Methodology

## The Operating Principle

**Define the test before you write the code.**

Success criteria are established before any planning or implementation. The system is validated against those criteria after implementation — not against a softened version designed to make the work pass.

This applies at every level: the baseline research, the source set, the update rhythm, the overall system.

---

## Two-Phase Operation

### Phase 1: Baseline (One-Time, Then Permanent)

Build comprehensive knowledge in all 10 categories up to the current date. This is the foundation — everything else layers on top of it.

**Baseline is complete when:** All 10 category files pass the criteria in `03-success-criteria.md → Component 1`.

**Baseline is never deleted.** It is updated (appended to, with dated sections) when the state of a field meaningfully changes, but the original baseline is preserved as the starting point.

**Who builds it:** Primarily AI-assisted deep research (Claude, Perplexity, NotebookLM) with Sanjay's active review and POV injection. The baseline is not "what AI says about X" — it is Sanjay's curated view of the state of X, informed by research.

---

### Phase 2: Periodic Updates (Ongoing, Layered on Baseline)

After the baseline is validated, a regular cadence adds new signals, developments, and POV evolution.

**Cadence by zone:**

| Zone | Daily touchpoint | Weekly synthesis | Monthly deep |
|------|-----------------|-----------------|--------------|
| Zone 1: Present Intelligence | Skim strong signal sources (10–15 min) | Add 3–5 tagged signals to update log | Review: has baseline changed? |
| Zone 2: Futures Intelligence | Skim weak signal sources (10 min) | Add tagged signals; note pattern shifts | Update futures POV if evidence warrants |
| Zone 3: Practitioner Toolkit | Use tools as part of normal work | Log notable tool insights (5 min) | Write one practitioner post |
| Zone 4: Experimenter's Lab | — | One experiment or learning (weekend or dedicated time) | Document experiment output |

**Updates do NOT rewrite the baseline.** They are stored in `updates/YYYY/` as dated entries. The system accumulates; it does not replace.

---

## Source Selection Methodology

Sources are not chosen by popularity. They are chosen by criteria.

### Before Adding a Source

Ask:
1. **Coverage:** Which of the 10 categories does this source serve?
2. **Perspective:** What type of voice is this — technologist, business strategist, academic, practitioner, contrarian?
3. **Signal density:** In the last 10 posts/episodes/articles, how many were strong or weak signals vs. noise?
4. **Uniqueness:** Does this source add something not already covered by existing sources?
5. **Sustainability:** Can I realistically consume this source at its publication frequency?

A source only enters the set if it passes all five.

### Source Review (Quarterly)

Every source is reviewed against the signal density criterion (60% minimum) each quarter. Sources that fall below are removed or placed on probation for one more cycle.

---

## Knowledge Processing Pipeline

Every item consumed passes through this sequence:

```
1. READ / WATCH / LISTEN
        ↓
2. CLASSIFY   Strong Signal / Weak Signal / Noise
        ↓ (discard Noise)
3. TAG        Which of the 10 categories does this belong to?
        ↓
4. EXTRACT    What is the signal? One sentence.
              What does it imply? One sentence.
              What is my reaction/POV? One sentence.
        ↓
5. STORE      Into the appropriate update log entry
        ↓
6. CONNECT    Does this connect to anything already in the baseline or prior signals?
              If yes — note the connection
```

Steps 1–3 happen during daily consumption. Steps 4–6 happen during weekly synthesis.

**Nothing enters the knowledge system without going through this pipeline.** Bookmarking is not processing. Reading is not processing. Processing requires steps 4–6.

---

## POV Development Process

The system exists to develop and refine an original point of view — not just accumulate facts.

**Monthly POV review:**
1. Open `zone2-futures-intelligence/03-long-arc-futures-pov.md`
2. Read the current stated positions
3. Ask: what new evidence from the past month challenges or supports each position?
4. Update: if evidence warrants a change, revise the position with a dated note explaining what changed and why

**The goal:** By the end of each year, the futures POV document reflects a genuinely evolved, evidence-grounded set of original positions — not a static list written once and never revisited.

---

## Citation Standard (Non-Negotiable)

Every source named in prose — in baseline research, in periodic updates, in intel cards, in publishing outputs — must carry a verifiable URL. Named-only citations ("McKinsey State of AI 2025" without a link) fail the credibility test this system exists to meet.

### Rules

1. **First mention of a substantive source in a document is a full inline markdown hyperlink.** Example:
   > [Peng et al. (GitHub, 2023)](https://arxiv.org/abs/2302.06590) showed ~26% productivity improvement…
2. **Every subsequent mention in the same document is followed by a footnote marker** `[^key]`, pointing to a definition in the `## Sources` section at the bottom.
3. **Every document ends with a `## Sources` section** (placed before `## Connections to Other Categories`) that groups footnote definitions by type — Papers & Reports, Benchmarks, Articles & Newsletters, People (Sources to Track), Organizations & Publications.
4. **"Substantive" sources** — papers, reports, named studies, benchmarks, articles, newsletters, Substack posts, and the people listed in the "Key Figures / Sources to Track" section. Do NOT link product names (GPT-4o, Claude 3.7, Gemini) or generic org mentions (Microsoft, Nvidia) without a specific claim attached.
5. **Never invent a URL.** If an authoritative source cannot be verified via HEAD-check, the sidecar entry stays `url: TODO` and the footnote renders `[needs-url]` until resolved. A visible gap beats a hallucinated link.

### Workflow

- For each document `<file>.md`, maintain a sidecar `<file>.sources.yaml` listing every substantive source as a structured entry (schema documented in `scripts/inject_sources.py`).
- Run `python3 scripts/inject_sources.py <file>.md` to (re)generate the inline links, footnote markers, and `## Sources` section from the sidecar. The script is idempotent — running it twice is a no-op.
- The sidecar YAML is the source-of-truth. URLs can be audited, updated, or replaced without re-editing prose.

This standard applies retroactively to baseline research and forward to all updates, intel cards, and publishing outputs.

---

## The "Not Fooling Yourself" Principle

Three specific failure modes to guard against:

1. **Consumption without synthesis** — reading/watching without forming a position. Set a rule: no item is "processed" until step 4 (extract) is done.

2. **Confirmation bias in source selection** — choosing sources that agree with existing beliefs. Maintain at least two credible contrarian voices in every zone.

3. **Backfilling criteria** — adjusting success criteria after the fact to make work "pass." The criteria in `03-success-criteria.md` are fixed at definition time. If the system fails, the system is fixed — not the criteria.
