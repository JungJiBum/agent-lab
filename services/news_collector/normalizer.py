from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, urlunsplit


def normalize_article(article: dict) -> dict:
    published = parsedate_to_datetime(article["published"])
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    url = urlsplit(article["url"])

    return {
        "title": article["title"].strip(),
        "url": urlunsplit((
            url.scheme.lower(),
            url.netloc.lower(),
            url.path,
            url.query,
            "",
        )),
        "published_at": published.isoformat(),
        "content": article["content"].strip(),
        "source": "aitimes",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }