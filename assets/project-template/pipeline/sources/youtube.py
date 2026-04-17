"""YouTube playlist source collector using YouTube Data API v3."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .base import SourceCollector, SourceItem

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
TOKEN_PATH = Path("youtube_token.json")


class YouTubeCollector(SourceCollector):
    """Fetches videos from a custom YouTube playlist."""

    source_type = "youtube"

    def __init__(self, playlist_id: str, client_id: str, client_secret: str):
        self.playlist_id = playlist_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._youtube = None

    def _get_credentials(self) -> Credentials:
        """Load saved credentials or run OAuth flow."""
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            if creds.valid:
                return creds
            if creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                TOKEN_PATH.write_text(creds.to_json())
                return creds

        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": ["http://localhost"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
        )
        creds = flow.run_local_server(port=0)

        # Save for reuse
        TOKEN_PATH.write_text(creds.to_json())
        logger.info("YouTube OAuth token saved to %s", TOKEN_PATH)
        return creds

    def _build_service(self):
        creds = self._get_credentials()
        return build("youtube", "v3", credentials=creds)

    def collect(self) -> list[SourceItem]:
        """Fetch all items from the configured playlist."""
        if not self.playlist_id:
            logger.warning("No YouTube playlist_id configured — skipping")
            return []

        youtube = self._build_service()
        items: list[SourceItem] = []

        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=self.playlist_id,
            maxResults=50,
        )

        while request:
            response = request.execute()

            for entry in response.get("items", []):
                snippet = entry["snippet"]
                title = snippet.get("title", "")

                # Skip deleted/private videos
                if title in ("Deleted video", "Private video"):
                    continue

                video_id = entry["contentDetails"]["videoId"]
                published_raw = snippet.get("publishedAt")
                published_at = None
                if published_raw:
                    published_at = datetime.fromisoformat(
                        published_raw.replace("Z", "+00:00")
                    )

                items.append(
                    SourceItem(
                        source_type="youtube",
                        source_id=video_id,
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        title=title,
                        author=snippet.get("videoOwnerChannelTitle", ""),
                        published_at=published_at,
                        description=snippet.get("description", ""),
                        thumbnail_url=(
                            snippet.get("thumbnails", {})
                            .get("high", {})
                            .get("url")
                        ),
                        raw_metadata={
                            "playlist_item_id": entry["id"],
                            "channel_id": snippet.get("videoOwnerChannelId", ""),
                        },
                    )
                )

            request = youtube.playlistItems().list_next(request, response)

        logger.info("YouTube collector found %d items in playlist", len(items))
        return items
