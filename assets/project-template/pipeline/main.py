"""Entry point: orchestrates the full pipeline run.

Usage:
    python -m pipeline.main
    python -m pipeline.main --config path/to/config.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from .artifacts import generate_all_artifacts_parallel
from .config import PipelineConfig, load_config
from .db import PipelineDB
from .notebooklm import NotebookLMWrapper
from .processor import process_new_items
from .prompts import get_audio_prompt, get_slide_prompt
from .scorer import score_item
from .sources.base import SourceItem
from .sources.youtube import YouTubeCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _build_instructions(config: PipelineConfig) -> dict[str, str]:
    """Build artifact_type → instructions mapping from config styles."""
    instructions: dict[str, str] = {}
    if "slides" in config.artifact_types:
        instructions["slides"] = get_slide_prompt(config.styles.slides)
    if "audio_overview" in config.artifact_types:
        instructions["audio_overview"] = get_audio_prompt(config.styles.audio)
    return instructions


def collect_all_sources(config: PipelineConfig) -> list[SourceItem]:
    """Run all enabled source collectors and return combined items."""
    all_items: list[SourceItem] = []

    # YouTube
    yt = config.sources.youtube
    if yt.enabled:
        if not yt.playlist_id:
            logger.warning("YouTube enabled but no playlist_id configured — skipping")
        elif not yt.client_id or not yt.client_secret:
            logger.warning("YouTube enabled but OAuth credentials missing — skipping")
        else:
            collector = YouTubeCollector(
                playlist_id=yt.playlist_id,
                client_id=yt.client_id,
                client_secret=yt.client_secret,
            )
            items = collector.collect()
            all_items.extend(items)

    # RSS (Phase 3 — stub)
    if config.sources.rss.enabled:
        logger.info("RSS source collection not yet implemented")

    return all_items


async def process_pending_items(
    config: PipelineConfig,
    db: PipelineDB,
    wrapper: NotebookLMWrapper,
) -> int:
    """Process pending items: create notebooks, generate & download artifacts.

    Returns count of successfully processed items.
    """
    pending = db.get_pending_items(limit=config.max_items_per_run)
    if not pending:
        logger.info("No pending items to process")
        return 0

    logger.info("Processing %d pending items (max_per_run=%d)", len(pending), config.max_items_per_run)
    artifact_instructions = _build_instructions(config)
    logger.info("Slide style: %s | Audio style: %s", config.styles.slides, config.styles.audio)
    done_count = 0

    for item in pending:
        # Score for tiered processing
        score, themes = score_item(item.title, item.description, item.author)

        if score < config.min_score_chat:
            logger.info("⊘ Skipping (score %d): %s", score, item.title)
            db.update_status(item.id, "skipped")
            continue

        logger.info("━━━ Processing: %s (score=%d, themes=%s)", item.title, score, themes)
        db.update_status(item.id, "processing")

        try:
            # Reuse existing notebook if this is a retry (prevents duplicates)
            if item.notebook_id:
                notebook_id = item.notebook_id
                logger.info("Reusing existing notebook: %s", notebook_id)
            else:
                notebook_id = await wrapper.create_notebook(item.title)
                db.update_status(item.id, "processing", notebook_id=notebook_id)
                await wrapper.add_source(notebook_id, item.url)
                item.notebook_id = notebook_id

            if score < config.min_score_full:
                # Chat-only: extract intel card, no artifacts
                logger.info("◐ Chat-only extraction (score %d < %d)", score, config.min_score_full)
                intel_card = await wrapper.extract_intel_card(notebook_id)
                db.save_intel_card(item.id, intel_card)
                logger.info("✓ Intel card extracted (themes: %s)", intel_card.get("themes", []))
            else:
                # Full processing: artifacts + intel card
                logger.info("● Full processing (score %d)", score)
                succeeded = await generate_all_artifacts_parallel(
                    wrapper=wrapper,
                    db=db,
                    item=item,
                    artifact_types=config.artifact_types,
                    artifact_instructions=artifact_instructions,
                    dual_slides=config.dual_slides,
                )
                logger.info("✓ Done: %s — artifacts: %s", item.title, list(succeeded.keys()))

            db.update_status(item.id, "done")
            done_count += 1

        except Exception as e:
            logger.error("✗ Failed: %s — %s", item.title, e)
            db.update_status(item.id, "failed", error_message=str(e))

        # Rate limit protection between items
        await asyncio.sleep(2)

    return done_count


async def run(config_path: str = "config.yaml", env_path: str = ".env") -> None:
    """Main pipeline run."""
    config = load_config(config_path, env_path)
    db = PipelineDB(config.db_path)
    db.connect()

    try:
        # Step 1: Collect from all sources
        logger.info("═══ Step 1: Collecting sources")
        all_items = collect_all_sources(config)
        logger.info("Collected %d total items from all sources", len(all_items))

        # Step 2: Deduplicate and save to DB
        logger.info("═══ Step 2: Processing new items")
        new_count = process_new_items(db, all_items)
        logger.info("Saved %d new items to database", new_count)

        # Step 3: Process pending items through NotebookLM
        logger.info("═══ Step 3: Generating artifacts via NotebookLM")
        wrapper = NotebookLMWrapper(storage_path=config.notebooklm_storage_path)
        try:
            await wrapper.connect()
            done_count = await process_pending_items(config, db, wrapper)
            logger.info("Successfully processed %d items", done_count)
        except Exception as e:
            if "auth" in str(e).lower() or "401" in str(e) or "403" in str(e):
                logger.error(
                    "NotebookLM authentication error. Please run: notebooklm login\n"
                    "Error: %s", e,
                )
            else:
                raise
        finally:
            await wrapper.close()

        # Summary
        stats = db.get_stats()
        logger.info("═══ Pipeline complete. Status: %s", stats)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Elite Research Pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--env", default=".env", help="Path to .env file")
    args = parser.parse_args()

    asyncio.run(run(config_path=args.config, env_path=args.env))


if __name__ == "__main__":
    main()
