import httpx

API_URL = "http://api:8000/api/news/ingest"


async def send_article(article: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(API_URL, json=article)
        response.raise_for_status()
        return response.json()