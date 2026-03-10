"""Generate artifacts in NotebookLM — all within a single notebook per item."""

from __future__ import annotations

import asyncio
import logging

from .db import ItemRow, PipelineDB
from .notebooklm import ARTIFACT_MAP, NotebookLMWrapper
from .prompts import get_slide_prompt, select_contextual_style

logger = logging.getLogger(__name__)


async def _generate_one(
    wrapper: NotebookLMWrapper,
    notebook_id: str,
    artifact_type: str,
    label: str,
    instructions: str | None = None,
) -> tuple[str, str | None]:
    """Generate a single artifact. Returns (label, error_or_None)."""
    try:
        logger.info("Generating %s ...", label)
        await wrapper.generate_artifact(
            notebook_id, artifact_type, instructions=instructions,
        )
        logger.info("✓ %s ready", label)
        return label, None
    except Exception as e:
        logger.error("✗ %s failed: %s", label, e)
        return label, str(e)


async def generate_all_artifacts_parallel(
    wrapper: NotebookLMWrapper,
    db: PipelineDB,
    item: ItemRow,
    artifact_types: list[str],
    artifact_instructions: dict[str, str] | None = None,
    dual_slides: bool = True,
    **_kwargs,
) -> dict[str, str]:
    """Generate ALL artifacts in parallel within a single notebook.

    Everything runs concurrently inside item.notebook_id:
      - Primary slides (playbook style from config)
      - Contextual slides (auto-selected style based on content)
      - Audio overview

    Returns dict of all succeeded artifact labels.
    """
    notebook_id = item.notebook_id
    instructions_map = artifact_instructions or {}
    tasks = []

    # Primary artifacts: slides + audio (inside the existing notebook)
    for artifact_type in artifact_types:
        if artifact_type not in ARTIFACT_MAP:
            logger.warning("Skipping unknown artifact type: %s", artifact_type)
            continue
        instructions = instructions_map.get(artifact_type)
        tasks.append(_generate_one(
            wrapper, notebook_id, artifact_type, artifact_type,
            instructions=instructions,
        ))

    # Contextual slides (second deck, same notebook, auto-selected style)
    if dual_slides and "slides" in artifact_types:
        style = select_contextual_style(item.title, item.description)
        contextual_instructions = get_slide_prompt(style)
        label = f"slides_{style}"
        logger.info("Contextual style auto-selected: %s (for: %s)", style, item.title)
        tasks.append(_generate_one(
            wrapper, notebook_id, "slides", label,
            instructions=contextual_instructions,
        ))

    if not tasks:
        return {}

    # Run everything in parallel within the same notebook
    logger.info("Launching %d artifact generations in parallel (notebook: %s)", len(tasks), notebook_id)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect results
    succeeded: dict[str, str] = {}
    failed: dict[str, str] = {}
    for result in results:
        if isinstance(result, Exception):
            logger.error("Parallel task raised exception: %s", result)
            continue
        label, error = result
        if error is None:
            succeeded[label] = "generated"
            db.record_download(item.id, label, f"notebooklm://{notebook_id}/{label}")
        else:
            failed[label] = error

    if failed:
        logger.warning("Some artifacts failed: %s", failed)
    if not succeeded and tasks:
        raise RuntimeError("All artifacts failed — check logs above")

    logger.info("All parallel generation complete: %d/%d artifacts succeeded", len(succeeded), len(tasks))

    # Extract intel card via NotebookLM chat (zero Claude tokens)
    try:
        logger.info("Extracting intel card via NotebookLM chat...")
        intel_card = await wrapper.extract_intel_card(notebook_id)
        db.save_intel_card(item.id, intel_card)
        succeeded["intel_card"] = "extracted"
        logger.info("✓ Intel card extracted (themes: %s)", intel_card.get("themes", []))
    except Exception as e:
        logger.warning("Intel card extraction failed (non-fatal): %s", e)

    return succeeded
