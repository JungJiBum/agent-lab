import feedparser
import httpx

RSS_URL = "https://cdn.aitimes.com/rss/gn_rss_allArticle.xml"


async def fetch_news(limit: int = 5) -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(RSS_URL)
        response.raise_for_status()

    feed = feedparser.parse(response.content)

    if feed.bozo:
        raise ValueError(f"RSS parsing failed: {feed.bozo_exception}")

    return [
        {
            "title": entry.get("title"),
            "url": entry.get("link"),
            "published": entry.get("published"),
            "summary": entry.get("summary"),
        }
        for entry in feed.entries[:limit]
    ]