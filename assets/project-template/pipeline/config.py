"""Load config.yaml + .env into typed dataclasses."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass
class YouTubeConfig:
    enabled: bool = True
    playlist_id: str = ""
    client_id: str = ""
    client_secret: str = ""


@dataclass
class RSSFeed:
    url: str
    name: str = ""


@dataclass
class RSSConfig:
    enabled: bool = False
    feeds: list[RSSFeed] = field(default_factory=list)


@dataclass
class RSSHubRoute:
    route: str
    name: str = ""


@dataclass
class RSSHubConfig:
    enabled: bool = False
    base_url: str = "http://localhost:1200"
    routes: list[RSSHubRoute] = field(default_factory=list)


@dataclass
class SourcesConfig:
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    rss: RSSConfig = field(default_factory=RSSConfig)
    rsshub: RSSHubConfig = field(default_factory=RSSHubConfig)


@dataclass
class StylesConfig:
    slides: str = "executive"
    audio: str = "deep_dive"


@dataclass
class PipelineConfig:
    max_items_per_run: int = 5
    artifacts_dir: str = "./artifacts"
    db_path: str = "./pipeline.db"
    artifact_types: list[str] = field(default_factory=lambda: ["audio_overview", "slides"])
    dual_slides: bool = True
    styles: StylesConfig = field(default_factory=StylesConfig)
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    notebooklm_storage_path: str | None = None
    min_score_full: int = 5       # Full processing (notebook + slides + audio)
    min_score_chat: int = 2       # Chat-only extraction (intel card, no artifacts)


def load_config(config_path: str = "config.yaml", env_path: str = ".env") -> PipelineConfig:
    """Load configuration from YAML file and environment variables."""
    load_dotenv(env_path)

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file) as f:
        raw = yaml.safe_load(f)

    pipeline = raw.get("pipeline", {})
    sources_raw = raw.get("sources", {})

    # YouTube config
    yt_raw = sources_raw.get("youtube", {})
    youtube = YouTubeConfig(
        enabled=yt_raw.get("enabled", True),
        playlist_id=yt_raw.get("playlist_id", ""),
        client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
    )

    # RSS config
    rss_raw = sources_raw.get("rss", {})
    rss_feeds = [RSSFeed(url=f["url"], name=f.get("name", "")) for f in (rss_raw.get("feeds") or [])]
    rss = RSSConfig(enabled=rss_raw.get("enabled", False), feeds=rss_feeds)

    # RSSHub config
    rsshub_raw = sources_raw.get("rsshub", {})
    rsshub_routes = [RSSHubRoute(route=r["route"], name=r.get("name", "")) for r in (rsshub_raw.get("routes") or [])]
    rsshub = RSSHubConfig(
        enabled=rsshub_raw.get("enabled", False),
        base_url=rsshub_raw.get("base_url", "http://localhost:1200"),
        routes=rsshub_routes,
    )

    # Styles config
    styles_raw = raw.get("styles", {})
    styles = StylesConfig(
        slides=styles_raw.get("slides", "executive"),
        audio=styles_raw.get("audio", "deep_dive"),
    )

    return PipelineConfig(
        max_items_per_run=pipeline.get("max_items_per_run", 5),
        artifacts_dir=pipeline.get("artifacts_dir", "./artifacts"),
        db_path=pipeline.get("db_path", "./pipeline.db"),
        artifact_types=raw.get("artifact_types", ["audio_overview", "slides"]),
        dual_slides=pipeline.get("dual_slides", True),
        styles=styles,
        sources=SourcesConfig(youtube=youtube, rss=rss, rsshub=rsshub),
        notebooklm_storage_path=os.getenv("NOTEBOOKLM_STORAGE_PATH"),
        min_score_full=pipeline.get("min_score_full", 5),
        min_score_chat=pipeline.get("min_score_chat", 2),
    )
