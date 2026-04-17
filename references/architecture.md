# Elite Research Pipeline — Architecture

## Data Flow

```
[YouTube "Research Queue" Playlist]  [RSS Feeds]  [Future Sources]
              │                          │               │
              ▼                          ▼               ▼
         youtube.py                   rss.py            ...
              │                          │               │
              └────────────┬─────────────┘───────────────┘
                           │
                     SourceItem (normalized dataclass)
                           │
                     processor.py (dedup, group)
                           │
                     db.py (SQLite — new/processing/done/failed)
                           │
                     notebooklm.py (create notebook → add source → generate artifacts)
                           │
                     artifacts.py (download to local folders)
                           │
                     artifacts/{date}/{slug}/ (audio, slides, metadata.json)
```

## Core Concepts

### SourceItem
Normalized representation of any content item:
```python
@dataclass
class SourceItem:
    source_type: str        # "youtube", "rss", "url"
    source_id: str          # unique ID (video_id, feed_entry_id, url hash)
    url: str                # canonical URL
    title: str
    author: str
    published_at: datetime | None
    description: str
    thumbnail_url: str | None
    raw_metadata: dict      # source-specific data
```

### Item Status Flow
```
new → processing → done
                 → failed (retry on next run)
```

### Pipeline Run
1. **Collect** — each SourceCollector fetches new items
2. **Normalize** — items converted to SourceItem
3. **Dedup** — check against DB by (source_type, source_id)
4. **Save** — new items inserted with status `new`
5. **Process** — up to `max_items_per_run` items:
   a. Create NotebookLM notebook
   b. Add source URL
   c. Generate configured artifact types
   d. Wait for completion
   e. Download artifacts to local folder
   f. Write metadata.json
   g. Mark item `done`
6. **Error handling** — on failure, mark item `failed` with error message

## Database Schema

### items
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| source_type | TEXT | "youtube", "rss", etc. |
| source_id | TEXT | Unique within source_type |
| url | TEXT | Canonical URL |
| title | TEXT | Content title |
| author | TEXT | Creator/channel name |
| published_at | TEXT | ISO 8601 timestamp |
| description | TEXT | Content description |
| thumbnail_url | TEXT | Thumbnail image URL |
| raw_metadata | TEXT | JSON blob |
| status | TEXT | new/processing/done/failed |
| error_message | TEXT | Last error (if failed) |
| notebook_id | TEXT | NotebookLM notebook ID |
| created_at | TEXT | When added to DB |
| updated_at | TEXT | Last status change |

**Unique constraint:** `(source_type, source_id)`

### artifact_downloads
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| item_id | INTEGER FK | References items.id |
| artifact_type | TEXT | audio_overview, slides, etc. |
| file_path | TEXT | Local path to downloaded file |
| downloaded_at | TEXT | When downloaded |

## Configuration

### config.yaml
```yaml
pipeline:
  max_items_per_run: 5
  artifacts_dir: "./artifacts"
  db_path: "./pipeline.db"

artifact_types:
  - audio_overview
  - slides

sources:
  youtube:
    enabled: true
    playlist_id: "PLxxxxxxxxxxxxxxxx"

  rss:
    enabled: false
    feeds: []
```

### .env
```
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
```

## Design Decisions

1. **One notebook per item** — focused artifacts, no cross-contamination
2. **SQLite** — zero infrastructure, crash recovery, idempotent reruns
3. **Async** — notebooklm-py is async; pipeline follows suit
4. **Rate limiting** — `max_items_per_run` (default 5) + sleep between operations
5. **Source independence** — NotebookLM can break; source collection always works
6. **Slug-based output dirs** — `artifacts/2026-03-08/my-video-title/`
