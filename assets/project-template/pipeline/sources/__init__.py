"""Source collectors package."""

from .base import SourceCollector, SourceItem
from .youtube import YouTubeCollector

__all__ = ["SourceCollector", "SourceItem", "YouTubeCollector"]
