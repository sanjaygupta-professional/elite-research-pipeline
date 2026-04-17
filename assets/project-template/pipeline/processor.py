"""Normalize, deduplicate, and save source items to the database."""

from __future__ import annotations

import logging

from .db import PipelineDB
from .sources.base import SourceItem

logger = logging.getLogger(__name__)


def process_new_items(db: PipelineDB, items: list[SourceItem]) -> int:
    """Deduplicate items against the DB and insert new ones.

    Returns the count of newly inserted items.
    """
    inserted = 0
    for item in items:
        row_id = db.insert_item(
            source_type=item.source_type,
            source_id=item.source_id,
            url=item.url,
            title=item.title,
            author=item.author,
            published_at=item.published_at.isoformat() if item.published_at else None,
            description=item.description,
            thumbnail_url=item.thumbnail_url,
            raw_metadata=item.raw_metadata,
        )
        if row_id > 0:
            inserted += 1
            logger.info("New item: %s — %s", item.source_type, item.title)
        else:
            logger.debug("Already seen: %s — %s", item.source_type, item.title)

    logger.info("Processed %d items → %d new", len(items), inserted)
    return inserted
