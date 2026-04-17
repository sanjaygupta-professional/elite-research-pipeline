# Signal Scoring Framework

*A structured approach to assess, filter, and rank signals across all categories — replacing intuition with repeatable judgment.*

## Why This Exists

The original signal classification (Strong / Weak / Noise) answers **"Is this real?"** but not **"Does this matter?"** or **"What should I do about it?"**

This framework adds five assessment dimensions that together produce a **signal profile** — not a single score (that would create false precision) but a structured judgment that makes the reasoning transparent, debatable, and updatable.

The goal: identify signals that are **uncommon but likely** — the top 20% that create disproportionate value for anyone positioning for the future. Signals that are real (not hype), accelerating (not plateauing), and unlock new possibilities (not incremental improvements).

---

## The Five Dimensions

### Dimension 1: Evidence Strength
*Is this real? Can I point to deployment, data, or measurable outcomes?*

| Score | Level | Criteria | Example |
|-------|-------|----------|---------|
| 1 | Theoretical | Paper or concept only. No working implementation | Quantum error correction at scale |
| 2 | Lab/demo | Working prototype in controlled conditions. Published by credible lab | GPT-o3 87.5% on ARC-AGI-1 (Dec 2024) |
| 3 | Early deployment | Real users at limited scale. Published results, not just claims | Copilot for Business in 500+ enterprise orgs |
| 4 | Scaled deployment | Multiple orgs, measurable production outcomes, third-party verification | GitHub Copilot 55K+ enterprise customers |
| 5 | Industry standard | Widespread, mature tooling, well-understood tradeoffs | Cloud computing, CI/CD pipelines |

**Rule:** Vendor announcements without independent verification cap at 2. Conference demos without production evidence cap at 2. Peer-reviewed research with reproduction starts at 3.

---

### Dimension 2: Trajectory Pattern
*Where is this on its growth curve? Inspired by Kurzweil's Law of Accelerating Returns — the key is recognizing which S-curve you're on, and whether a new one is starting.*

| Pattern | Description | What to watch | Implication |
|---------|-------------|---------------|-------------|
| **Emerging** | New capability, few data points, steep early curve starting | Frequency of new entrants, speed of benchmark improvements | High uncertainty, high potential. Track closely |
| **Accelerating** | Exponential phase. Each period shows 2x+ improvement in cost, capability, or adoption | Doubling times, cost curves, benchmark trajectories | **Maximum strategic value — position now** |
| **Maturing** | Growth rate slowing. Approaching practical limits of current paradigm | Diminishing benchmark gains, consolidation, "good enough" discourse | Optimize and harvest. Don't over-invest |
| **Shifting** | Old paradigm plateauing while new paradigm emerges alongside | New architectures appearing, old leaders pivoting, "X is dead" discourse | **Capability unlock moment.** The transition zone where most value is created and most incumbents miss the turn |

**Key insight from Kurzweil:** When one S-curve plateaus, look for the next paradigm starting underneath. Moore's Law was not the first S-curve for computing — it was the fifth. The shift between curves is where predictions go wrong if you only extrapolate the current curve.

---

### Dimension 3: Capability Unlock
*Does this enable things that weren't possible before? This is the most forward-looking dimension — it assesses not what something does, but what it makes possible for everything else.*

| Score | Level | Test question | Example |
|-------|-------|---------------|---------|
| 1 | Incremental | Does this make an existing process faster/cheaper? | GPT-4 Turbo — faster, cheaper, same paradigm |
| 2 | New application | Does this let a new audience do something previously restricted to experts? | Code Copilot enabling non-engineers to prototype |
| 3 | Category creation | Does this make an entire class of workflows possible that didn't exist? | Reasoning models → agentic workflows. MCP → tool-use standardization |
| 4 | Paradigm shift | Does this restructure how industries, roles, or institutions function? | If AGI-level autonomy emerges → organizational redesign at scale |

**The unlock question:** "What becomes possible *only because* of this, that was not possible before it existed?"

A signal with Evidence Strength 2 but Capability Unlock 4 is a weak signal *about a paradigm shift* — exactly the kind of thing Category 6 (Weak Signal Watch) should track. Low confidence, massive implication.

---

### Dimension 4: Hype-Reality Gap
*Is the attention proportional to the substance? Informed by Gartner's Hype Cycle phases, but expressed as a gap measure rather than a lifecycle stage.*

| Rating | Description | Detection heuristics |
|--------|-------------|---------------------|
| **Grounded** | Claims ≈ evidence. Deployments confirm narrative | Independent benchmarks exist. Multiple orgs report similar results. Discourse is about tradeoffs, not potential |
| **Ahead of itself** | Real progress, but claims outpace deployment | Impressive demos. "Coming soon" > "We deployed." 10x more conference talks than production case studies |
| **Peak hype** | Massive attention, minimal production evidence | Everyone talking, few building. Media echo chamber. Vendor announcements recycled as "news." No independent benchmarks |
| **Post-hype** | Attention dropped, but real builders still shipping | Fewer headlines, more GitHub commits. Startups failing, but survivors growing. Honest assessments replacing breathless coverage |

**Hype filter rule:** Signals rated **Peak hype** are excluded from the "Uncommon but Likely" shortlist regardless of other dimension scores. They may still be tracked in baseline research for completeness, but are not actionable until the hype-reality gap closes.

**Contrarian note:** Some of the highest-value signals live in **Post-hype** — technologies the media has declared dead but builders are quietly scaling. This is where conventional wisdom is most wrong.

---

### Dimension 5: Time Horizon to Impact
*When does this become actionable — not when it's announced, but when it changes decisions?*

| Horizon | Window | Confidence basis | Action stance |
|---------|--------|-----------------|---------------|
| **Now** | 0–6 months | Deployed and measurable today | Act. Build on this. Advise clients now |
| **Near** | 6–18 months | In pilot/beta, clear path to production | Prepare. Develop POV. Start experiments |
| **Medium** | 18–36 months | Early deployment, scaling challenges remain | Watch actively. Identify leading indicators |
| **Far** | 3–7 years | Lab-stage or theoretical, but trajectory plausible | Track quarterly. Scenario-plan. Don't bet the house |

**Rule of thumb:** Confidence decreases with horizon length. Evidence Strength 4+ signals with Near/Now horizons are high-confidence. Evidence Strength 2 signals with Far horizon are speculative — they belong in Zone 2 futures intelligence, not Zone 1 present intelligence.

---

## The Signal Profile

Every signal assessed in the system gets a five-element profile, not a single number:

```
Signal: [name]
Profile: E[1-5] T[Em/Ac/Ma/Sh] U[1-4] H[Gr/Ah/Ph/Poh] Z[Now/Near/Med/Far]
Summary: [one sentence — what this means and why it matters]
```

**Example profiles:**

```
Signal: Reasoning models enabling agentic task completion
Profile: E3 T-Accelerating U3 H-Ahead Z-Near
Summary: Real deployment evidence (SWE-bench, Devin, Claude Code) but production 
         reliability still unproven. Unlocks autonomous multi-step workflows.

Signal: Local model fine-tuning for enterprise-specific tasks  
Profile: E3 T-Emerging U2 H-Post-hype Z-Now
Summary: Quietly maturing after LLaMA hype cycle. QLoRA/PEFT makes it practical. 
         New application: domain-specific models at fraction of API cost.

Signal: Quantum computing for practical ML workloads
Profile: E1 T-Emerging U4 H-Peak-hype Z-Far  
Summary: Paradigm-shifting if achieved, but no evidence of near-term ML application.
         Filtered out of actionable shortlist.
```

---

## Ranked Shortlist: "Uncommon but Likely"

Each baseline category produces a **ranked top 3–5 signals** that pass the Uncommon but Likely filter:

### Filter criteria (all must hold):
1. **Evidence Strength ≥ 3** — not theoretical; real deployment, credible first-party data, or documented institutional adoption exists
2. **Trajectory = Accelerating, Shifting, or Emerging (with E ≥ 3)** — not plateau. Emerging trajectory qualifies only when evidence strength is 3+. The logic: a signal in its earliest phase can still be "likely" if a credible first-mover has already built the future-state case (e.g., Moderna's Chief People & Digital Technology Officer role)
3. **Capability Unlock ≥ 2** — enables something new, not just incremental
4. **Hype-Reality Gap ≠ Peak hype** — substance exceeds noise
5. **Not mainstream consensus** — most people haven't positioned for this yet

**Strictness note (April 2026 refinement):** The earlier version excluded all Emerging trajectories, which turned out to disqualify some of the highest-signal early insights. The refined rule preserves strict Evidence discipline (weak signals with E 1-2 must go to the Emerging Signals section or Category 06 Weak Signal Watch) while allowing evidenced-but-early signals to be ranked.

### Ranking within the shortlist:

Signals that pass all five filters are ranked by **strategic leverage** — a qualitative judgment call combining:
- How many *other* categories this signal connects to (cross-category amplification)
- How asymmetric the upside is (small bet, large payoff if right)
- How actionable it is for the reader (can they do something about it this quarter?)

### Output format per category:

```markdown
## Uncommon but Likely — [Category Name]
*Ranked signals that are real, accelerating, enabling, and under-recognized*

### 1. [Signal name]
**Profile:** E[x] T[x] U[x] H[x] Z[x]
**What's happening:** [2-3 sentences — the evidence]
**Why it matters:** [what this unlocks]  
**What most people miss:** [the uncommon insight]
**If true, optimize by:** [specific action for the reader]
**Watch for:** [what would confirm or disconfirm in next 6 months]

### 2. [Signal name]
...
```

---

## How This Integrates with the Existing System

### Relationship to Strong / Weak / Noise classification

The original classification remains as the **intake filter** — it decides whether something enters the system at all:
- **Noise** → Discarded. Never scored.
- **Weak signal** → Entered into system, scored on all five dimensions. Expected to have low Evidence Strength (1-2) but may score high on Capability Unlock.
- **Strong signal** → Entered into system, scored on all five dimensions. Expected to have Evidence Strength ≥ 3.

The five-dimension scoring is applied *after* intake, to signals that have already passed the noise filter.

### Changes to the baseline template

Each baseline category file gains a new section after "Open Questions":

```markdown
## Signal Assessment
### Ranked Shortlist: Uncommon but Likely (top 3-5)
[ranked signal profiles with full detail]

### Additional Strong Signals (Evidence ≥ 4, established)
[profiles — these are important but widely known]

### Emerging Signals to Watch (Evidence 1-2, high Unlock potential)
[profiles — low confidence, track for corroboration]

### Filtered Out (Peak hype or noise)
[brief list with reason for exclusion]
```

### Periodic updates

When new signals are assessed during routine incremental updates, they get the same five-dimension profile. If a signal's profile changes materially (e.g., Evidence Strength moves from 2 → 4, or Hype-Reality shifts from Peak → Post-hype), the baseline entry is annotated with the dated update.

---

## Source Authority Tiers

Signals must be grounded in sources. The quality of the source constrains the maximum Evidence Strength score.

### Tier 1: Authoritative (for baselining)
*Original researchers, institutional reports, benchmark creators, people with first-party data*

| Source type | Examples | Max Evidence Score |
|-------------|---------|-------------------|
| AI research labs (published results) | OpenAI, Anthropic, Google DeepMind, Meta FAIR, xAI, DeepSeek, Baidu AI | 5 |
| University research groups | Stanford HAI/CRFM, MIT CSAIL, CMU, Berkeley AI | 5 |
| Peer-reviewed benchmarks | HELM, ARC-AGI, SWE-bench, MMLU, Papers With Code | 5 |
| Management consultancies (original research) | Accenture, McKinsey Global Institute, BCG Henderson, Deloitte | 4 |
| Industry analyst firms (with methodology) | Gartner, Forrester, IDC | 4 |
| Academic journals | Harvard Business Review, MIT Sloan Management Review, Nature, Science | 5 |
| Practitioner-researchers | Mollick (Wharton), Davenport (Babson), Brynjolfsson (Stanford) | 4 |

### Tier 2: Quality Synthesizers (for incremental updates)
*Skilled interpreters who read widely, process intelligently, and add original perspective*

| Source type | Examples | Max Evidence Score |
|-------------|---------|-------------------|
| Researcher newsletters/blogs | Import AI (Jack Clark), The Batch (Andrew Ng), One Useful Thing (Mollick) | 3 (unless citing Tier 1 data, then inherits) |
| Technical thought leaders | Karpathy (YouTube/X), Chollet (Substack), Marcus (blog) | 3 |
| Industry insiders | a16z AI (Casado), Sequoia AI, Bessemer | 3 |
| Quality Substacks/newsletters | Stratechery (Ben Thompson), Nathan Benaich (State of AI), Zvi Mowshowitz | 3 |
| Practitioner YouTube/podcasts | AI-focused channels with demonstrated expertise | 2 |

### Excluded: Hype Amplifiers
*Engagement-driven content with no original analysis or data*

- Reposted vendor announcements without commentary
- "Top 10 AI tools" listicles
- Engagement-farming X/Twitter threads with no sources
- Vendor marketing disguised as thought leadership
- Media articles that cite only other media articles

**Rule:** If a source's signal density falls below 60% (per the methodology doc), it moves to probation and is re-evaluated at the quarterly source review.

---

## Failure Modes to Guard Against

1. **Scoring inflation** — Resist the urge to rate every signal as high-unlock. Most signals are incremental (Unlock = 1). That's fine. The framework's value comes from the rare 3s and 4s.
2. **Consensus disguised as insight** — "AI will transform enterprise" is not an Uncommon but Likely signal. It's consensus. The insight is *how specifically* and *through what mechanism*.
3. **Recency bias** — This week's announcement feels more important than it is. Apply the hype filter honestly.
4. **Confirmation bias** — Maintain at least 2 credible contrarian voices per zone (already in methodology doc — enforced here by requiring "What most people miss" for every shortlisted signal).
5. **False precision** — The five dimensions produce a profile, not a formula. Two reasonable people can disagree on whether Evidence Strength is 3 or 4. That's fine. The value is in making the reasoning explicit, not in the number.
