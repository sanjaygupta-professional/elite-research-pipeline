# pipeline/scorer.py
"""Score content relevance before NotebookLM processing.

Assigns a 0-10 score based on title/description keyword matching
against research themes. Zero Claude tokens — pure Python.
"""

from __future__ import annotations

import logging

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
