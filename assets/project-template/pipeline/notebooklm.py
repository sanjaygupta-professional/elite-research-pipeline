"""Async wrapper around notebooklm-py: create notebooks, add sources, generate artifacts."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from notebooklm import NotebookLMClient
from notebooklm.exceptions import RPCError

logger = logging.getLogger(__name__)

# Map config artifact names → (generate_method, download_method, file_extension)
ARTIFACT_MAP: dict[str, tuple[str, str, str]] = {
    "audio_overview": ("generate_audio", "download_audio", ".mp3"),
    "slides": ("generate_slide_deck", "download_slide_deck", ".pdf"),
    "mind_map": ("generate_mind_map", "download_mind_map", ".json"),
    "infographic": ("generate_infographic", "download_infographic", ".png"),
}

MAX_RETRIES = 3
BASE_DELAY = 5  # seconds


@dataclass
class GeneratedArtifact:
    artifact_type: str
    file_extension: str
    task_id: str | None  # None for mind_map (returns directly)


async def _retry_async(coro_factory, description: str):
    """Retry an async operation with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            return await coro_factory()
        except RPCError as e:
            delay = BASE_DELAY * (2 ** attempt)
            if attempt < MAX_RETRIES - 1:
                logger.warning(
                    "%s failed (attempt %d/%d): %s — retrying in %ds",
                    description, attempt + 1, MAX_RETRIES, e, delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error("%s failed after %d attempts: %s", description, MAX_RETRIES, e)
                raise


class NotebookLMWrapper:
    """High-level wrapper for NotebookLM operations."""

    def __init__(self, storage_path: str | None = None):
        self.storage_path = storage_path
        self._client: NotebookLMClient | None = None

    async def connect(self) -> None:
        if self.storage_path:
            self._client = await NotebookLMClient.from_storage(self.storage_path)
        else:
            self._client = await NotebookLMClient.from_storage()
        await self._client.__aenter__()

    async def close(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    @property
    def client(self) -> NotebookLMClient:
        if self._client is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._client

    async def create_notebook(self, title: str) -> str:
        """Create a notebook and return its ID."""
        nb = await _retry_async(
            lambda: self.client.notebooks.create(title),
            f"Create notebook '{title}'",
        )
        logger.info("Created notebook: %s (id=%s)", title, nb.id)
        return nb.id

    async def add_source(self, notebook_id: str, url: str) -> str:
        """Add a URL (YouTube, web, etc.) as a source. Returns source ID.

        notebooklm-py uses add_url() for all URL types including YouTube.
        """
        src = await _retry_async(
            lambda: self.client.sources.add_url(notebook_id, url),
            f"Add source: {url}",
        )
        logger.info("Added source: %s (id=%s)", url, src.id)
        # Give NotebookLM time to process the source
        await asyncio.sleep(5)
        return src.id

    async def generate_artifact(
        self,
        notebook_id: str,
        artifact_type: str,
        instructions: str | None = None,
        **extra_kwargs,
    ) -> GeneratedArtifact:
        """Generate a single artifact type with optional instructions.

        Args:
            notebook_id: The notebook to generate from.
            artifact_type: One of the keys in ARTIFACT_MAP.
            instructions: Free-text prompt/instructions for generation quality.
            **extra_kwargs: Additional API params (e.g. orientation, detail_level for infographics).
        """
        if artifact_type not in ARTIFACT_MAP:
            raise ValueError(
                f"Unknown artifact type: {artifact_type}. "
                f"Known types: {list(ARTIFACT_MAP.keys())}"
            )

        gen_method, _, ext = ARTIFACT_MAP[artifact_type]
        method = getattr(self.client.artifacts, gen_method)

        # Build kwargs — pass instructions if supported and provided
        kwargs: dict = dict(extra_kwargs)
        if instructions and artifact_type in ("audio_overview", "slides", "infographic"):
            kwargs["instructions"] = instructions
        if instructions:
            logger.info("Using custom instructions for %s (%d chars)", artifact_type, len(instructions))

        # Mind map returns data directly (no task_id / polling)
        if artifact_type == "mind_map":
            await _retry_async(
                lambda: method(notebook_id, **kwargs),
                f"Generate {artifact_type}",
            )
            return GeneratedArtifact(artifact_type=artifact_type, file_extension=ext, task_id=None)

        status = await _retry_async(
            lambda: method(notebook_id, **kwargs),
            f"Generate {artifact_type}",
        )
        logger.info("Started generation: %s (task_id=%s)", artifact_type, status.task_id)

        # Wait for completion — audio can take 10+ minutes
        timeout = 900 if artifact_type == "audio_overview" else 600
        await self.client.artifacts.wait_for_completion(
            notebook_id, status.task_id, timeout=timeout, poll_interval=10,
        )
        logger.info("Artifact ready: %s", artifact_type)

        return GeneratedArtifact(
            artifact_type=artifact_type, file_extension=ext, task_id=status.task_id,
        )

    async def download_artifact(
        self, notebook_id: str, artifact_type: str, output_path: str
    ) -> None:
        """Download a completed artifact to the given path."""
        if artifact_type not in ARTIFACT_MAP:
            raise ValueError(f"Unknown artifact type: {artifact_type}")

        _, dl_method, _ = ARTIFACT_MAP[artifact_type]
        method = getattr(self.client.artifacts, dl_method)

        await _retry_async(
            lambda: method(notebook_id, output_path),
            f"Download {artifact_type}",
        )
        logger.info("Downloaded %s → %s", artifact_type, output_path)

    async def chat_ask(
        self, notebook_id: str, question: str, conversation_id: str | None = None,
    ) -> tuple[str, str]:
        """Ask NotebookLM a question about notebook content.

        Returns (answer_text, conversation_id) for follow-ups.
        """
        result = await _retry_async(
            lambda: self.client.chat.ask(notebook_id, question, conversation_id=conversation_id),
            f"Chat ask: {question[:50]}...",
        )
        logger.info("Chat response: %d chars", len(result.answer))
        return result.answer, result.conversation_id

    async def extract_intel_card(self, notebook_id: str) -> dict:
        """Extract a Futures Intelligence Card via NotebookLM chat.

        Zero Claude tokens — uses NotebookLM's built-in AI.
        Returns structured dict with signals, possibilities, etc.
        """
        prompt = (
            "Analyze this content through a futures/foresight lens. "
            "Respond in EXACTLY this structured format with no preamble:\n\n"
            "SIGNALS:\n"
            "- [observable fact or data point 1]\n"
            "- [observable fact or data point 2]\n"
            "- [up to 5 total]\n\n"
            "POSSIBILITIES:\n"
            "- [future scenario this enables 1] | PROBABILITY: [High/Medium/Low/Emerging] | TIMEFRAME: [e.g. 6-12 months]\n"
            "- [future scenario 2] | PROBABILITY: [level] | TIMEFRAME: [range]\n"
            "- [up to 3 total]\n\n"
            "IMPLICATIONS:\n"
            "- [who is affected and how 1]\n"
            "- [up to 3 total]\n\n"
            "ADVISORY:\n"
            "- [actionable recommendation 1]\n"
            "- [up to 2 total]\n\n"
            "THEMES: [comma-separated theme tags, e.g. AI Agents, Enterprise AI, Future of Work]"
        )

        answer, _ = await self.chat_ask(notebook_id, prompt)
        return self._parse_intel_card(answer)

    @staticmethod
    def _parse_intel_card(text: str) -> dict:
        """Parse structured text response into intel card dict."""
        card: dict = {
            "signals": [],
            "possibilities": [],
            "implications": [],
            "advisory": [],
            "themes": [],
            "raw_response": text,
        }

        current_section = None
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            upper = line.upper().rstrip(":")
            if upper == "SIGNALS":
                current_section = "signals"
            elif upper == "POSSIBILITIES":
                current_section = "possibilities"
            elif upper == "IMPLICATIONS":
                current_section = "implications"
            elif upper == "ADVISORY":
                current_section = "advisory"
            elif upper.startswith("THEMES"):
                # Parse comma-separated themes
                themes_text = line.split(":", 1)[-1].strip() if ":" in line else ""
                card["themes"] = [t.strip() for t in themes_text.split(",") if t.strip()]
                current_section = None
            elif line.startswith("- ") and current_section:
                item = line[2:].strip()
                if current_section == "possibilities":
                    if "|" in item:
                        parts = [p.strip() for p in item.split("|")]
                        entry = {"scenario": parts[0]}
                        for part in parts[1:]:
                            if part.upper().startswith("PROBABILITY:"):
                                entry["probability"] = part.split(":", 1)[1].strip()
                            elif part.upper().startswith("TIMEFRAME:"):
                                entry["timeframe"] = part.split(":", 1)[1].strip()
                        card["possibilities"].append(entry)
                    else:
                        card["possibilities"].append({"scenario": item})
                else:
                    card[current_section].append(item)

        return card
