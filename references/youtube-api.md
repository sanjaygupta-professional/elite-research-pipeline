# YouTube Data API v3 — Playlist Access Patterns

## Overview

We use the YouTube Data API v3 to read items from a custom "Research Queue" playlist.
**Why not Watch Later?** Google restricted API access to Watch Later playlists years ago.

---

## OAuth 2.0 Setup (One-Time)

### 1. Create Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., "Elite Research Pipeline")
3. Enable **YouTube Data API v3** under APIs & Services → Library

### 2. Create OAuth Credentials
1. APIs & Services → Credentials → Create Credentials → OAuth client ID
2. Application type: **Desktop app**
3. Download the JSON — save as `client_secret.json`
4. Set `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` in `.env`

### 3. Configure OAuth Consent Screen
1. APIs & Services → OAuth consent screen
2. User type: **External** (or Internal if using Workspace)
3. Add scope: `https://www.googleapis.com/auth/youtube.readonly`
4. Add yourself as a test user

---

## API Patterns

### Authentication Flow (google-auth-oauthlib)
```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# First run: browser-based OAuth
flow = InstalledAppFlow.from_client_config(
    {"installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }},
    scopes=SCOPES,
)
credentials = flow.run_local_server(port=0)

# Save token for reuse
token_data = {
    "token": credentials.token,
    "refresh_token": credentials.refresh_token,
    "token_uri": credentials.token_uri,
    "client_id": credentials.client_id,
    "client_secret": credentials.client_secret,
    "scopes": credentials.scopes,
}
# Save to ~/.elite-research/youtube_token.json
```

### Fetching Playlist Items
```python
youtube = build("youtube", "v3", credentials=credentials)

def get_playlist_items(youtube, playlist_id, max_results=50):
    items = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=min(max_results, 50),  # API max per page
    )
    while request and len(items) < max_results:
        response = request.execute()
        for item in response["items"]:
            items.append({
                "video_id": item["contentDetails"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["videoOwnerChannelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url"),
                "playlist_item_id": item["id"],
            })
        request = youtube.playlistItems().list_next(request, response)
    return items
```

### Finding Playlist ID
- Go to your playlist on YouTube
- The URL contains `list=PLxxxxxx` — that's the playlist ID
- Or use the API: `youtube.playlists().list(part="snippet", mine=True)`

---

## Quotas

- Default quota: **10,000 units/day**
- `playlistItems.list`: **1 unit** per call
- Each call returns up to 50 items
- For a 100-item playlist: 2 API calls = 2 units
- Very generous for our use case

---

## Key Considerations

1. **Token refresh** — `google-auth` handles refresh tokens automatically. Store the refresh token securely.
2. **Deleted videos** — playlist items for deleted videos have title "Deleted video". Filter these out.
3. **Private videos** — similarly titled "Private video". Filter out.
4. **Pagination** — use `list_next()` for playlists with >50 items.
5. **Rate limiting** — extremely unlikely to hit with our usage pattern. No special handling needed.
