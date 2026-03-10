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
