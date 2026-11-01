import httpx
from bs4 import BeautifulSoup


async def scrape_article(url: str) -> str:
    async with httpx.AsyncClient(
        timeout=15,
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # AI타임스 기사 본문 영역
    article = soup.select_one("#article-view-content-div")

    if article is None:
        raise ValueError(f"Article content not found: {url}")

    # 본문과 관계없는 요소 제거
    for element in article.select(
        "script, style, iframe, figure, .ad, .advertisement"
    ):
        element.decompose()

    return article.get_text(separator="\n", strip=True)