# Futures Intelligence System — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Elite Research Pipeline from a content processor into a Futures Intelligence System — multi-source collection, zero-token extraction via NotebookLM chat, cross-source synthesis, and professional publishing for thought leadership under the "Possibilities with Probabilities" brand.

**Architecture:** Four layers — Source Collection (zero tokens), Processing (NotebookLM API), Extraction (NotebookLM chat, zero Claude tokens), and Publishing (on-demand, Claude + installed skills). Pre-filtering scores items by relevance before any NotebookLM processing.

**Tech Stack:** Python 3.12 async, notebooklm-py v0.3.3 (chat + artifacts APIs), feedparser (RSS), SQLite, RSSHub (Docker, for Twitter/X/Reddit/HN), installed skills (linkedin-content, market-research-reports, brand-identity, writing-x-posts, newsletter)

---

## Phase 1: Pre-Filter + NotebookLM Chat Extraction (Zero Claude Tokens)

### Task 1: Add Relevance Scorer

**Files:**
- Create: `pipeline/scorer.py`
- Modify: `pipeline/config.py`
- Test: manual verification with known titles

**Step 1: Create the scorer module**

```python
# pipeline/scorer.py
"""Score content relevance before NotebookLM processing.

Assigns a 0-10 score based on title/description keyword matching
against research themes. Zero Claude tokens — pure Python.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Research themes with weighted keywords
# Higher weight = stronger signal for "Possibilities with Probabilities"
THEMES: dict[str, dict[str, int]] = {
    "ai_agents": {
        "ai agent": 3, "autonomous": 2, "agentic": 3, "tool use": 2,
        "agent framework": 3, "multi-agent": 3, "agent loop": 2,
        "orchestration": 2, "agent sdk": 2,
    },
    "generative_ai": {
        "generative ai": 3, "llm": 2, "large language model": 3,
        "foundation model": 2, "gpt": 1, "claude": 2, "gemini": 1,
        "diffusion": 1, "multimodal": 2, "reasoning": 2,
    },
    "enterprise_ai": {
        "enterprise": 2, "digital transformation": 3, "ai strategy": 3,
        "ai governance": 3, "responsible ai": 2, "ai adoption": 2,
        "ai maturity": 2, "cto": 2, "cio": 2,
    },
    "future_of_work": {
        "future of work": 3, "automation": 2, "augmentation": 2,
        "workforce": 2, "reskilling": 2, "human-ai": 3,
        "collaboration": 1, "productivity": 1,
    },
    "org_development": {
        "organization development": 3, "org design": 3, "culture": 1,
        "leadership": 2, "change management": 2, "team": 1,
        "organizational": 2, "transformation": 2,
    },
}

# Trusted channels/authors auto-boost score
TRUSTED_SOURCES: set[str] = {
    # Add your trusted YouTube channels, blog authors, etc.
    # These get +3 to their score automatically
}

# Minimum duration in seconds (skip clips < 3 min)
MIN_DURATION_SECONDS = 180


def score_item(
    title: str,
    description: str = "",
    author: str = "",
    duration_seconds: int | None = None,
) -> tuple[int, list[str]]:
    """Score an item's relevance to research themes.

    Returns:
        (score 0-10, list of matched theme names)
    """
    # Duration filter
    if duration_seconds is not None and duration_seconds < MIN_DURATION_SECONDS:
        logger.debug("Skipping short content (%ds): %s", duration_seconds, title)
        return 0, []

    text = f"{title} {description}".lower()
    total_score = 0
    matched_themes: list[str] = []

    for theme, keywords in THEMES.items():
        theme_score = 0
        for keyword, weight in keywords.items():
            if keyword.lower() in text:
                theme_score += weight
        if theme_score > 0:
            matched_themes.append(theme)
            total_score += theme_score

    # Trusted source boost
    if author.lower() in {s.lower() for s in TRUSTED_SOURCES}:
        total_score += 3

    # Cap at 10
    score = min(total_score, 10)
    logger.debug("Score %d for: %s (themes: %s)", score, title, matched_themes)
    return score, matched_themes
```

**Step 2: Add score thresholds to config**

In `pipeline/config.py`, add to PipelineConfig:
```python
    min_score_full: int = 5       # Full processing (notebook + slides + audio)
    min_score_chat: int = 2       # Chat-only extraction (intel card, no artifacts)
```

In `load_config()`, read from YAML:
```python
    min_score_full=pipeline.get("min_score_full", 5),
    min_score_chat=pipeline.get("min_score_chat", 2),
```

**Step 3: Commit**

```bash
git add pipeline/scorer.py pipeline/config.py
git commit -m "feat: add relevance scorer for pre-filtering content"
```

---

### Task 2: Add NotebookLM Chat Wrapper for Extraction

**Files:**
- Modify: `pipeline/notebooklm.py`

**Step 1: Add chat methods to NotebookLMWrapper**

Add to the `NotebookLMWrapper` class in `notebooklm.py`:

```python
    async def chat_ask(
        self, notebook_id: str, question: str, conversation_id: str | None = None,
    ) -> tuple[str, str]:
        """Ask NotebookLM a question about notebook content.

        Returns (answer_text, conversation_id) for follow-ups.
        """
        result = await _retry_async(
            lambda: self.client.chat.ask(notebook_id, question, conversation_id=conversation_id),
            f"Chat ask: {question[:50]}...",
        )
        logger.info("Chat response: %d chars", len(result.answer))
        return result.answer, result.conversation_id

    async def extract_intel_card(self, notebook_id: str) -> dict:
        """Extract a Futures Intelligence Card via NotebookLM chat.

        Zero Claude tokens — uses NotebookLM's built-in AI.
        Returns structured dict with signals, possibilities, etc.
        """
        prompt = (
            "Analyze this content through a futures/foresight lens. "
            "Respond in EXACTLY this structured format with no preamble:\n\n"
            "SIGNALS:\n"
            "- [observable fact or data point 1]\n"
            "- [observable fact or data point 2]\n"
            "- [up to 5 total]\n\n"
            "POSSIBILITIES:\n"
            "- [future scenario this enables 1] | PROBABILITY: [High/Medium/Low/Emerging] | TIMEFRAME: [e.g. 6-12 months]\n"
            "- [future scenario 2] | PROBABILITY: [level] | TIMEFRAME: [range]\n"
            "- [up to 3 total]\n\n"
            "IMPLICATIONS:\n"
            "- [who is affected and how 1]\n"
            "- [up to 3 total]\n\n"
            "ADVISORY:\n"
            "- [actionable recommendation 1]\n"
            "- [up to 2 total]\n\n"
            "THEMES: [comma-separated theme tags, e.g. AI Agents, Enterprise AI, Future of Work]"
        )

        answer, _ = await self.chat_ask(notebook_id, prompt)
        return self._parse_intel_card(answer)

    @staticmethod
    def _parse_intel_card(text: str) -> dict:
        """Parse structured text response into intel card dict."""
        card: dict = {
            "signals": [],
            "possibilities": [],
            "implications": [],
            "advisory": [],
            "themes": [],
            "raw_response": text,
        }

        current_section = None
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            upper = line.upper().rstrip(":")
            if upper == "SIGNALS":
                current_section = "signals"
            elif upper == "POSSIBILITIES":
                current_section = "possibilities"
            elif upper == "IMPLICATIONS":
                current_section = "implications"
            elif upper == "ADVISORY":
                current_section = "advisory"
            elif upper.startswith("THEMES"):
                # Parse comma-separated themes
                themes_text = line.split(":", 1)[-1].strip() if ":" in line else ""
                card["themes"] = [t.strip() for t in themes_text.split(",") if t.strip()]
                current_section = None
            elif line.startswith("- ") and current_section:
                item = line[2:].strip()
                if current_section == "possibilities" and "|" in item:
                    parts = [p.strip() for p in item.split("|")]
                    entry = {"scenario": parts[0]}
                    for part in parts[1:]:
                        if part.upper().startswith("PROBABILITY:"):
                            entry["probability"] = part.split(":", 1)[1].strip()
                        elif part.upper().startswith("TIMEFRAME:"):
                            entry["timeframe"] = part.split(":", 1)[1].strip()
                    card["possibilities"].append(entry)
                else:
                    card[current_section].append(item)

        return card
```

**Step 2: Commit**

```bash
git add pipeline/notebooklm.py
git commit -m "feat: add NotebookLM chat extraction for zero-token intel cards"
```

---

### Task 3: Add Intel Card Storage to Database

**Files:**
- Modify: `pipeline/db.py`

**Step 1: Add intel_cards table**

Add to `_create_tables()` in `PipelineDB`:

```sql
CREATE TABLE IF NOT EXISTS intel_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    signals TEXT NOT NULL DEFAULT '[]',
    possibilities TEXT NOT NULL DEFAULT '[]',
    implications TEXT NOT NULL DEFAULT '[]',
    advisory TEXT NOT NULL DEFAULT '[]',
    themes TEXT NOT NULL DEFAULT '[]',
    raw_response TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(item_id)
);
```

**Step 2: Add methods to PipelineDB**

```python
    def save_intel_card(self, item_id: int, card: dict) -> int:
        """Save an intel card for an item. Returns card ID."""
        import json
        cur = self._conn.execute(
            """INSERT OR REPLACE INTO intel_cards
               (item_id, signals, possibilities, implications, advisory, themes, raw_response)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                item_id,
                json.dumps(card.get("signals", [])),
                json.dumps(card.get("possibilities", [])),
                json.dumps(card.get("implications", [])),
                json.dumps(card.get("advisory", [])),
                json.dumps(card.get("themes", [])),
                card.get("raw_response", ""),
            ),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_intel_cards(self, limit: int = 50, theme: str | None = None) -> list[dict]:
        """Get intel cards, optionally filtered by theme."""
        import json
        if theme:
            rows = self._conn.execute(
                """SELECT ic.*, i.title, i.url FROM intel_cards ic
                   JOIN items i ON ic.item_id = i.id
                   WHERE ic.themes LIKE ?
                   ORDER BY ic.created_at DESC LIMIT ?""",
                (f"%{theme}%", limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT ic.*, i.title, i.url FROM intel_cards ic
                   JOIN items i ON ic.item_id = i.id
                   ORDER BY ic.created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        cols = [d[0] for d in self._conn.execute("SELECT * FROM intel_cards LIMIT 0").description]
        cols += ["title", "url"]
        result = []
        for row in rows:
            d = dict(zip(cols, row))
            for key in ("signals", "possibilities", "implications", "advisory", "themes"):
                d[key] = json.loads(d[key]) if isinstance(d[key], str) else d[key]
            result.append(d)
        return result

    def get_recent_themes(self, days: int = 30) -> dict[str, int]:
        """Get theme frequency counts from recent intel cards."""
        import json
        rows = self._conn.execute(
            """SELECT themes FROM intel_cards
               WHERE created_at > datetime('now', ?)""",
            (f"-{days} days",),
        ).fetchall()
        counts: dict[str, int] = {}
        for (themes_json,) in rows:
            for theme in json.loads(themes_json):
                counts[theme] = counts.get(theme, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))
```

**Step 3: Commit**

```bash
git add pipeline/db.py
git commit -m "feat: add intel_cards table and query methods"
```

---

### Task 4: Integrate Scorer + Chat Extraction into Pipeline

**Files:**
- Modify: `pipeline/artifacts.py`
- Modify: `pipeline/main.py`
- Modify: `pipeline/single_url.py`

**Step 1: Add intel card extraction to artifacts.py**

Add at the end of `generate_all_artifacts_parallel()`, after artifact generation succeeds:

```python
    # Extract intel card via NotebookLM chat (zero Claude tokens)
    try:
        logger.info("Extracting intel card via NotebookLM chat...")
        intel_card = await wrapper.extract_intel_card(notebook_id)
        db.save_intel_card(item.id, intel_card)
        succeeded["intel_card"] = "extracted"
        logger.info("✓ Intel card extracted (themes: %s)", intel_card.get("themes", []))
    except Exception as e:
        logger.warning("Intel card extraction failed (non-fatal): %s", e)
```

**Step 2: Add tiered processing to main.py**

In `process_pending_items()`, add scoring before the processing loop.
After fetching pending items, score each and split into tiers:

```python
    from .scorer import score_item

    # Score and tier items
    for item in pending:
        score, themes = score_item(item.title, item.description, item.author)
        if score < config.min_score_chat:
            logger.info("⊘ Skipping (score %d): %s", score, item.title)
            db.update_status(item.id, "skipped")
            continue

        if score < config.min_score_full:
            # Chat-only: create notebook, extract intel card, no artifacts
            logger.info("◐ Chat-only (score %d): %s", score, item.title)
            # ... create notebook, add source, extract intel card only
        else:
            # Full processing: notebook + artifacts + intel card
            logger.info("● Full processing (score %d): %s", score, item.title)
            # ... existing full pipeline
```

**Step 3: Update single_url.py**

Single URL always gets full processing (user explicitly chose this URL), so just add intel card extraction after artifact generation. Same pattern as Step 1.

**Step 4: Add "skipped" status to db.py**

Add "skipped" to the valid status values. Items with status "skipped" can be reviewed and manually promoted.

**Step 5: Commit**

```bash
git add pipeline/artifacts.py pipeline/main.py pipeline/single_url.py pipeline/db.py
git commit -m "feat: tiered processing with scorer + chat extraction"
```

---

## Phase 2: RSS + RSSHub Source Collection

### Task 5: Add RSS Source Collector

**Files:**
- Create: `pipeline/sources/rss.py`
- Modify: `pipeline/config.py`
- Modify: `pipeline/main.py`

**Step 1: Create RSS collector**

```python
# pipeline/sources/rss.py
"""RSS/Atom feed collector using feedparser."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime

import feedparser

from .base import SourceCollector, SourceItem

logger = logging.getLogger(__name__)


class RSSCollector(SourceCollector):
    source_type = "rss"

    def __init__(self, feed_url: str, feed_name: str = ""):
        self.feed_url = feed_url
        self.feed_name = feed_name

    def collect(self) -> list[SourceItem]:
        logger.info("Fetching RSS: %s (%s)", self.feed_name or self.feed_url, self.feed_url)
        feed = feedparser.parse(self.feed_url)

        items = []
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url:
                continue

            source_id = hashlib.sha256(url.encode()).hexdigest()[:16]
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])

            items.append(SourceItem(
                source_type=self.source_type,
                source_id=source_id,
                url=url,
                title=entry.get("title", url),
                author=entry.get("author", self.feed_name),
                published_at=published,
                description=entry.get("summary", ""),
                raw_metadata={"feed_url": self.feed_url, "feed_name": self.feed_name},
            ))

        logger.info("Collected %d items from %s", len(items), self.feed_name or self.feed_url)
        return items
```

**Step 2: Add RSS feeds to config and collection logic**

In `main.py`, replace the RSS stub with actual collection using `RSSCollector`.

**Step 3: Commit**

```bash
git add pipeline/sources/rss.py pipeline/config.py pipeline/main.py
git commit -m "feat: add RSS/Atom feed source collector"
```

---

### Task 6: Add RSSHub Integration for Twitter/X, Reddit, HN

**Files:**
- Create: `pipeline/sources/rsshub.py`
- Modify: `pipeline/config.py`

**Step 1: Create RSSHub source**

RSSHub generates RSS feeds from Twitter lists, Reddit subreddits, HackerNews, etc.
It runs as a Docker container. The collector simply reads its RSS output.

```python
# pipeline/sources/rsshub.py
"""RSSHub-powered source collector (Twitter/X, Reddit, HN, etc.)."""

from __future__ import annotations

import logging

from .rss import RSSCollector

logger = logging.getLogger(__name__)


class RSSHubCollector(RSSCollector):
    """Wraps RSSHub-generated RSS feeds.

    RSSHub converts social media into RSS. Example routes:
    - Twitter list:  http://localhost:1200/twitter/list/user/listname
    - Subreddit:     http://localhost:1200/reddit/subreddit/MachineLearning
    - HackerNews:    http://localhost:1200/hackernews/best
    - arXiv:         http://localhost:1200/arxiv/search_query=ai+agents
    """
    source_type = "rsshub"

    def __init__(self, rsshub_base: str, route: str, feed_name: str = ""):
        url = f"{rsshub_base.rstrip('/')}/{route.lstrip('/')}"
        super().__init__(feed_url=url, feed_name=feed_name or route)
```

**Step 2: Add RSSHub config**

In `config.py`, add:
```python
@dataclass
class RSSHubConfig:
    enabled: bool = False
    base_url: str = "http://localhost:1200"
    routes: list[dict] = field(default_factory=list)
    # Each route: {"route": "twitter/list/user/listname", "name": "AI Twitter List"}
```

**Step 3: Add to config.yaml**

```yaml
sources:
  rsshub:
    enabled: true
    base_url: "http://localhost:1200"
    routes:
      - route: "twitter/list/youruser/ai-researchers"
        name: "AI Researchers (Twitter)"
      - route: "reddit/subreddit/MachineLearning/hot"
        name: "r/MachineLearning"
      - route: "hackernews/best"
        name: "HN Best"
```

**Step 4: Commit**

```bash
git add pipeline/sources/rsshub.py pipeline/config.py
git commit -m "feat: add RSSHub collector for Twitter/Reddit/HN"
```

---

## Phase 3: Publishing Templates (Minimal Token Usage)

### Task 7: Add Futures Intel Card Templates

**Files:**
- Create: `pipeline/templates.py`

**Step 1: Create template-based publishing**

Zero-token publishing for routine posts. Templates are filled from intel card data.

```python
# pipeline/templates.py
"""Zero-token publishing templates.

Fill intel card data into pre-built templates for LinkedIn, X, newsletter.
Only use Claude (via skills) for deep analysis pieces.
"""

from __future__ import annotations


def linkedin_post(card: dict, source_title: str, source_url: str) -> str:
    """Generate a LinkedIn post from an intel card. Zero tokens."""
    possibilities = card.get("possibilities", [])
    if not possibilities:
        return ""

    top = possibilities[0]
    scenario = top.get("scenario", "")
    probability = top.get("probability", "Medium")
    timeframe = top.get("timeframe", "12-24 months")

    advisory = card.get("advisory", [])
    advisory_text = advisory[0] if advisory else "Monitor this space closely."

    themes = card.get("themes", [])
    hashtags = " ".join(f"#{t.replace(' ', '')}" for t in themes[:3])

    return f"""What if {scenario.lower().rstrip('.')}?

Probability: {probability} | Timeframe: {timeframe}

{advisory_text}

Source: {source_title}

#PossibilitiesWithProbabilities {hashtags}
"""


def x_post(card: dict, source_title: str) -> str:
    """Generate an X/Twitter post from an intel card. Zero tokens."""
    signals = card.get("signals", [])
    possibilities = card.get("possibilities", [])
    if not signals or not possibilities:
        return ""

    top_signal = signals[0]
    top_possibility = possibilities[0]
    probability = top_possibility.get("probability", "Medium")

    return f"""Signal: {top_signal}

Possibility: {top_possibility.get('scenario', '')}
Probability: {probability}

#PossibilitiesWithProbabilities"""


def weekly_digest_markdown(cards: list[dict], week_label: str) -> str:
    """Generate a weekly digest from multiple intel cards. Zero tokens."""
    lines = [f"# Futures Intelligence Digest — {week_label}\n"]

    # Group by theme
    theme_cards: dict[str, list[dict]] = {}
    for card in cards:
        for theme in card.get("themes", ["Uncategorized"]):
            theme_cards.setdefault(theme, []).append(card)

    for theme, themed in sorted(theme_cards.items()):
        lines.append(f"\n## {theme}\n")
        for card in themed:
            for p in card.get("possibilities", []):
                prob = p.get("probability", "?")
                tf = p.get("timeframe", "?")
                lines.append(f"- **{p.get('scenario', '')}** [{prob}, {tf}]")

    # Advisory summary
    lines.append("\n## Action Items\n")
    for card in cards:
        for a in card.get("advisory", []):
            lines.append(f"- {a}")

    return "\n".join(lines)
```

**Step 2: Commit**

```bash
git add pipeline/templates.py
git commit -m "feat: add zero-token publishing templates for LinkedIn, X, digest"
```

---

### Task 8: Add CLI Commands for Publishing + Review

**Files:**
- Create: `pipeline/cli.py`

**Step 1: Create unified CLI**

```python
# pipeline/cli.py
"""CLI commands for the Futures Intelligence System."""

from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .db import PipelineDB
from .templates import linkedin_post, x_post, weekly_digest_markdown


def cmd_intel(args):
    """Show recent intel cards."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        cards = db.get_intel_cards(limit=args.limit, theme=args.theme)
        for card in cards:
            print(f"\n{'='*60}")
            print(f"Title: {card['title']}")
            print(f"URL:   {card['url']}")
            print(f"Themes: {', '.join(card['themes'])}")
            print(f"\nSignals:")
            for s in card["signals"]:
                print(f"  - {s}")
            print(f"\nPossibilities:")
            for p in card["possibilities"]:
                if isinstance(p, dict):
                    print(f"  - {p.get('scenario', p)} [{p.get('probability', '?')}, {p.get('timeframe', '?')}]")
                else:
                    print(f"  - {p}")
            print(f"\nAdvisory:")
            for a in card["advisory"]:
                print(f"  - {a}")
    finally:
        db.close()


def cmd_draft(args):
    """Generate a draft post from an intel card."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        cards = db.get_intel_cards(limit=1)
        if not cards:
            print("No intel cards found.")
            return
        card = cards[0]
        if args.format == "linkedin":
            print(linkedin_post(card, card["title"], card["url"]))
        elif args.format == "x":
            print(x_post(card, card["title"]))
    finally:
        db.close()


def cmd_digest(args):
    """Generate a weekly digest."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        cards = db.get_intel_cards(limit=50)
        print(weekly_digest_markdown(cards, args.week or "This Week"))
    finally:
        db.close()


def cmd_themes(args):
    """Show trending themes."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        themes = db.get_recent_themes(days=args.days)
        for theme, count in themes.items():
            print(f"  {count:3d}x  {theme}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Futures Intelligence System")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--env", default=".env")
    sub = parser.add_subparsers(dest="command")

    # intel
    p = sub.add_parser("intel", help="Show recent intel cards")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--theme", help="Filter by theme")

    # draft
    p = sub.add_parser("draft", help="Generate a draft post")
    p.add_argument("format", choices=["linkedin", "x"])

    # digest
    p = sub.add_parser("digest", help="Generate weekly digest")
    p.add_argument("--week", help="Week label")

    # themes
    p = sub.add_parser("themes", help="Show trending themes")
    p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"intel": cmd_intel, "draft": cmd_draft, "digest": cmd_digest, "themes": cmd_themes}[args.command](args)


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add pipeline/cli.py
git commit -m "feat: add CLI for intel cards, drafts, digests, themes"
```

---

## Phase 4: Incremental Weekly Synthesis

### Task 9: Add Weekly Synthesis (Delta-Only)

**Files:**
- Create: `pipeline/synthesis.py`

**Step 1: Create incremental synthesis**

This is the ONE place we optionally use Claude (Haiku) — but only on the delta of new cards since last synthesis. Can also be done via NotebookLM by creating a "synthesis notebook" with multiple sources.

```python
# pipeline/synthesis.py
"""Weekly synthesis — connect themes across intel cards.

Option A: Zero-token — template-based digest from intel cards
Option B: Minimal-token — Haiku processes only NEW cards since last synthesis
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from .db import PipelineDB
from .templates import weekly_digest_markdown

logger = logging.getLogger(__name__)


def generate_weekly_digest(db: PipelineDB) -> str:
    """Generate a weekly digest from recent intel cards. Zero tokens."""
    cards = db.get_intel_cards(limit=50)
    week_label = datetime.now().strftime("Week of %B %d, %Y")
    return weekly_digest_markdown(cards, week_label)
```

**Step 2: Commit**

```bash
git add pipeline/synthesis.py
git commit -m "feat: add weekly synthesis module"
```

---

## Implementation Order Summary

| Task | What | Claude Tokens | Priority |
|------|------|--------------|----------|
| 1 | Relevance Scorer | Zero | High |
| 2 | NotebookLM Chat Extraction | Zero | High |
| 3 | Intel Card DB Storage | Zero | High |
| 4 | Integrate Scorer + Extraction | Zero | High |
| 5 | RSS Source Collector | Zero | Medium |
| 6 | RSSHub for Twitter/Reddit/HN | Zero | Medium |
| 7 | Publishing Templates | Zero | Medium |
| 8 | CLI Commands | Zero | Medium |
| 9 | Weekly Synthesis | Zero (template) or Minimal (Haiku) | Low |

**Total Claude token cost for the entire system: effectively $0/month for routine operation.**
Claude is only used on-demand when you invoke publishing skills for deep analysis pieces.

---

## Config Evolution

```yaml
pipeline:
  max_items_per_run: 10
  db_path: "./pipeline.db"
  dual_slides: true
  min_score_full: 5              # NEW: Full processing threshold
  min_score_chat: 2              # NEW: Chat-only extraction threshold

artifact_types:
  - slides
  - audio_overview

styles:
  slides: "japanese_minimal"
  audio: "deep_dive"

sources:
  youtube:
    enabled: true
    playlist_id: "PLxxxxxx"

  rss:
    enabled: true
    feeds:
      - url: "https://stratechery.com/feed/"
        name: "Stratechery"
      - url: "https://www.oneusefulthing.org/feed"
        name: "One Useful Thing"
      - url: "https://jack-clark.net/feed/"
        name: "Import AI"

  rsshub:
    enabled: true
    base_url: "http://localhost:1200"
    routes:
      - route: "twitter/list/youruser/ai-futures"
        name: "AI Futures (Twitter)"
      - route: "reddit/subreddit/MachineLearning/hot"
        name: "r/MachineLearning"
      - route: "hackernews/best"
        name: "HN Best"
```
