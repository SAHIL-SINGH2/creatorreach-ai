from __future__ import annotations
from pathlib import Path
from typing import Iterable
import os
import requests
import pandas as pd

REQUIRED_COLUMNS = [
    "name", "platforms", "followers", "niche", "content_themes",
    "contact_email", "profile_url", "engagement_rate_pct"
]


def load_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def discover_from_csv(path: str | Path, limit: int = 50) -> pd.DataFrame:
    """Use a human/externally sourced dataset as the discovery input; no values are fabricated."""
    df = load_csv(path).copy()
    df["followers"] = pd.to_numeric(df["followers"], errors="coerce")
    return df.head(limit).copy()


class YouTubeDiscovery:
    """Optional live discovery using the official YouTube Data API v3."""
    endpoint = "https://www.googleapis.com/youtube/v3/search"
    channels_endpoint = "https://www.googleapis.com/youtube/v3/channels"

    def __init__(self, api_key: str | None = None, timeout: int = 20):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is required for live YouTube discovery")

    def search_channels(self, queries: Iterable[str], max_per_query: int = 50) -> pd.DataFrame:
        rows, seen = [], set()
        for q in queries:
            params = {"part": "snippet", "q": q, "type": "channel", "maxResults": min(max_per_query, 50), "key": self.api_key}
            r = requests.get(self.endpoint, params=params, timeout=self.timeout)
            r.raise_for_status()
            for item in r.json().get("items", []):
                cid = item.get("id", {}).get("channelId")
                if not cid or cid in seen:
                    continue
                seen.add(cid)
                rows.append({"channel_id": cid, "name": item.get("snippet", {}).get("title", ""),
                             "profile_url": f"https://www.youtube.com/channel/{cid}",
                             "description": item.get("snippet", {}).get("description", "")})
        if not rows:
            return pd.DataFrame()
        details = []
        for i in range(0, len(rows), 50):
            ids = ",".join(x["channel_id"] for x in rows[i:i+50])
            params = {"part": "snippet,statistics", "id": ids, "key": self.api_key}
            r = requests.get(self.channels_endpoint, params=params, timeout=self.timeout)
            r.raise_for_status()
            details.extend(r.json().get("items", []))
        by_id = {x["id"]: x for x in details}
        out = []
        for row in rows:
            item = by_id.get(row["channel_id"], {})
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            subs = pd.to_numeric(stats.get("subscriberCount"), errors="coerce")
            out.append({
                "name": snippet.get("title", row["name"]),
                "handle": "",
                "platforms": "YouTube",
                "followers": subs,
                "engagement_rate_pct": pd.NA,
                "er_source": "Not Found",
                "niche": "Unclassified",
                "content_themes": snippet.get("description", "")[:500],
                "contact_email": "Not Found",
                "email_status": "not_found",
                "email_source": "Not Found",
                "profile_url": row["profile_url"],
                "city_state": "Not Found",
                "discovered_via": "YouTube Data API v3",
            })
        return pd.DataFrame(out)
