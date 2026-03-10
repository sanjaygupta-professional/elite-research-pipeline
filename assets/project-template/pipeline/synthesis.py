# pipeline/synthesis.py
"""Weekly synthesis — connect themes across intel cards.

Option A: Zero-token — template-based digest from intel cards
Option B: Minimal-token — Haiku processes only NEW cards since last synthesis
"""

from __future__ import annotations

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
