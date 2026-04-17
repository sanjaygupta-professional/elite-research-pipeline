"""Abstract base class for source collectors and the shared SourceItem dataclass."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SourceItem:
    """Normalized representation of any content item from any source."""

    source_type: str  # "youtube", "rss", "url"
    source_id: str  # unique within source_type (video_id, entry_id, url hash)
    url: str
    title: str
    author: str = ""
    published_at: datetime | None = None
    description: str = ""
    thumbnail_url: str | None = None
    raw_metadata: dict = field(default_factory=dict)


class SourceCollector(ABC):
    """Base class for all content source collectors.

    Subclasses must set `source_type` as a class attribute and implement `collect()`.
    """

    source_type: str

    @abstractmethod
    def collect(self) -> list[SourceItem]:
        """Fetch and return new items from this source."""
        ...
