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
