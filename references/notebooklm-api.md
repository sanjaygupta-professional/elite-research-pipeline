# notebooklm-py API Reference

**Package:** `notebooklm-py` (v0.3.3) — unofficial Python client for Google NotebookLM
**Repo:** [github.com/teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py)
**Python:** >=3.10 | **Fully async**

---

## Authentication

### Login (one-time, requires GUI)
```bash
pip install "notebooklm-py[browser]"
playwright install chromium
notebooklm login   # Opens Chromium, log in to Google manually
```

Saves cookies to `~/.notebooklm/storage_state.json`. Session expires every few weeks — re-run `notebooklm login`.

### Using in Python
```python
from notebooklm import NotebookLMClient

async with await NotebookLMClient.from_storage() as client:
    # ... use client
```

Auth lookup order:
1. Explicit `path` arg to `from_storage(path)`
2. `NOTEBOOKLM_AUTH_JSON` env var
3. `$NOTEBOOKLM_HOME/storage_state.json`
4. `~/.notebooklm/storage_state.json`

---

## Client Structure

```python
client.notebooks   # NotebooksAPI
client.sources     # SourcesAPI
client.artifacts   # ArtifactsAPI
client.chat        # ChatAPI
```

---

## Key Methods

### Notebooks
```python
nb = await client.notebooks.create("My Notebook")  # → Notebook(id, title, ...)
nbs = await client.notebooks.list()                 # → list[Notebook]
await client.notebooks.delete(nb.id)
```

### Sources
```python
src = await client.sources.add_youtube(nb.id, "https://youtube.com/watch?v=...")
src = await client.sources.add_url(nb.id, "https://example.com/article")
src = await client.sources.add_text(nb.id, "Title", "content...")
srcs = await client.sources.list(nb.id)
```

`Source` dataclass: `id`, `title`, `url`, `created_at`, `.kind` (SourceType enum).

### Artifacts — Generation
All generation methods return `GenerationStatus` with a `task_id`:

```python
# Audio overview
status = await client.artifacts.generate_audio(
    nb.id,
    source_ids=[src.id],        # optional: subset of sources
    instructions="focus on key takeaways",
    audio_format="DEEP_DIVE",   # DEEP_DIVE | BRIEF | CRITIQUE | DEBATE
    audio_length="DEFAULT",     # SHORT | DEFAULT | LONG
    language=None               # auto-detect
)

# Slides
status = await client.artifacts.generate_slide_deck(
    nb.id,
    source_ids=None,
    slide_format="DETAILED_DECK",   # DETAILED_DECK | PRESENTER_SLIDES
    slide_length="DEFAULT"          # DEFAULT | SHORT
)

# Mind map
mind_map = await client.artifacts.generate_mind_map(nb.id)  # Returns dict directly

# Infographic
status = await client.artifacts.generate_infographic(
    nb.id,
    orientation="LANDSCAPE",    # LANDSCAPE | PORTRAIT | SQUARE
    detail_level="STANDARD"     # CONCISE | STANDARD | DETAILED
)
```

### Artifacts — Wait & Download
```python
# Wait for completion (polls internally)
final = await client.artifacts.wait_for_completion(
    nb.id, status.task_id,
    timeout=300,        # seconds
    poll_interval=5     # seconds between polls
)

# Download
await client.artifacts.download_audio(nb.id, "output.mp3")
await client.artifacts.download_slide_deck(nb.id, "slides.pdf")
await client.artifacts.download_infographic(nb.id, "infographic.png")
await client.artifacts.download_mind_map(nb.id, "mindmap.json")
```

If `artifact_id` is omitted, downloads the first completed artifact of that type.

---

## Error Handling

```python
from notebooklm.exceptions import (
    RPCError,                # Base for all API errors
    SourceAddError,          # Failed to add source
    SourceNotFoundError,
    SourceProcessingError,
    SourceTimeoutError,
    ArtifactNotFoundError,
    ArtifactNotReadyError,
    ArtifactDownloadError,
    ArtifactParseError,
)
```

---

## Gotchas

1. **Session expiry** — cookies expire every few weeks. Detect auth errors, prompt user to re-run `notebooklm login`.
2. **Rate limits** — add `asyncio.sleep(2)` between batch operations. Daily/hourly quotas for generation.
3. **Download URLs expire** within hours — download immediately after generation.
4. **Unofficial API** — uses undocumented Google batchexecute RPCs. Can break on Google changes.
5. **Twitter/X URLs** — get incorrectly parsed. Pre-fetch content and add as text instead.
6. **Playwright only for login** — all API calls use httpx. Can authenticate on GUI machine, copy storage_state.json to headless server.
