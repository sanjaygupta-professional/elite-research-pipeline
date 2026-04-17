"""Process a single URL through the pipeline.

Usage:
    python -m pipeline.single_url "https://www.youtube.com/watch?v=abc123"
    python -m pipeline.single_url "https://example.com/article" --title "My Article"
    python -m pipeline.single_url "https://youtu.be/abc123" --config path/to/config.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import re
import urllib.request
import urllib.error

from .artifacts import generate_all_artifacts_parallel
from .config import load_config
from .db import PipelineDB
from .notebooklm import NotebookLMWrapper
from .processor import process_new_items
from .prompts import get_audio_prompt, get_slide_prompt
from .sources.base import SourceItem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def extract_source_id(url: str) -> tuple[str, str]:
    """Extract source_type and source_id from a URL.

    For YouTube URLs, extracts the video ID.
    For other URLs, uses a hash of the URL.

    Returns:
        (source_type, source_id)
    """
    # YouTube: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID
    yt_patterns = [
        r"(?:youtube\.com/watch\?.*v=)([\w-]{11})",
        r"(?:youtu\.be/)([\w-]{11})",
        r"(?:youtube\.com/embed/)([\w-]{11})",
    ]
    for pattern in yt_patterns:
        match = re.search(pattern, url)
        if match:
            return "youtube", match.group(1)

    # Non-YouTube URL: use URL hash as source_id
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    return "url", url_hash


def fetch_title(url: str) -> str | None:
    """Fetch a human-readable title for a URL.

    Uses YouTube oEmbed for YouTube URLs (no auth needed).
    Falls back to HTML <title> tag for other URLs.
    Returns None if title cannot be fetched.
    """
    # YouTube oEmbed — fast, no auth
    source_type, _ = extract_source_id(url)
    if source_type == "youtube":
        oembed_url = f"https://www.youtube.com/oembed?url={urllib.request.quote(url, safe='')}&format=json"
        try:
            with urllib.request.urlopen(oembed_url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                title = data.get("title")
                if title:
                    logger.info("Fetched title: %s", title)
                    return title
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            logger.warning("Could not fetch YouTube title via oEmbed: %s", e)

    # Generic URL — try HTML <title>
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read(16384).decode("utf-8", errors="ignore")
            match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                logger.info("Fetched title: %s", title)
                return title
    except Exception as e:
        logger.warning("Could not fetch page title: %s", e)

    return None


async def run_single(
    url: str,
    title: str | None = None,
    config_path: str = "config.yaml",
    env_path: str = ".env",
) -> None:
    """Process a single URL through the pipeline."""
    config = load_config(config_path, env_path)
    db = PipelineDB(config.db_path)
    db.connect()

    try:
        source_type, source_id = extract_source_id(url)
        display_title = title or fetch_title(url) or url

        # Check for duplicates
        if db.item_exists(source_type, source_id):
            logger.info("Already in database: %s — skipping", display_title)
            return

        # Insert into DB
        item = SourceItem(
            source_type=source_type,
            source_id=source_id,
            url=url,
            title=display_title,
        )
        new_count = process_new_items(db, [item])
        if new_count == 0:
            logger.info("Item already exists — skipping")
            return

        # Build instructions from config styles
        instructions: dict[str, str] = {}
        if "slides" in config.artifact_types:
            instructions["slides"] = get_slide_prompt(config.styles.slides)
        if "audio_overview" in config.artifact_types:
            instructions["audio_overview"] = get_audio_prompt(config.styles.audio)

        logger.info("Slide style: %s | Audio style: %s", config.styles.slides, config.styles.audio)

        # Connect to NotebookLM and process
        wrapper = NotebookLMWrapper(storage_path=config.notebooklm_storage_path)
        try:
            await wrapper.connect()

            pending = db.get_pending_items(limit=1)
            if not pending:
                logger.info("No pending items")
                return

            pending_item = pending[0]
            logger.info("━━━ Processing: %s", pending_item.title)
            db.update_status(pending_item.id, "processing")

            # Create notebook (or reuse if retrying)
            if pending_item.notebook_id:
                notebook_id = pending_item.notebook_id
                logger.info("Reusing existing notebook: %s", notebook_id)
            else:
                notebook_id = await wrapper.create_notebook(pending_item.title)
                db.update_status(pending_item.id, "processing", notebook_id=notebook_id)
                await wrapper.add_source(notebook_id, pending_item.url)
                pending_item.notebook_id = notebook_id

            # Generate ALL artifacts in parallel
            succeeded = await generate_all_artifacts_parallel(
                wrapper=wrapper,
                db=db,
                item=pending_item,
                artifact_types=config.artifact_types,
                artifact_instructions=instructions,
                dual_slides=config.dual_slides,
            )

            db.update_status(pending_item.id, "done")
            logger.info("✓ Done: %s — artifacts: %s", pending_item.title, list(succeeded.keys()))

        except Exception as e:
            if pending:
                db.update_status(pending[0].id, "failed", error_message=str(e))
            if "auth" in str(e).lower() or "401" in str(e) or "403" in str(e):
                logger.error("NotebookLM auth error. Run: notebooklm login")
            else:
                logger.error("Failed: %s", e)
                raise
        finally:
            await wrapper.close()

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Process a single URL through the Elite Research Pipeline"
    )
    parser.add_argument("url", help="URL to process (YouTube link, article, etc.)")
    parser.add_argument("--title", help="Custom title (default: uses the URL)")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--env", default=".env", help="Path to .env file")
    args = parser.parse_args()

    asyncio.run(run_single(
        url=args.url,
        title=args.title,
        config_path=args.config,
        env_path=args.env,
    ))


if __name__ == "__main__":
    main()
