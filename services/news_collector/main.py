from fastapi import FastAPI, Query
from rss import fetch_news
from scraper import scrape_article
from normalizer import normalize_article
from sender import send_article

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

# @app.get("/collect/test")
# async def collect_test():
#     articles = await fetch_news(limit=1)

#     for article in articles:
#         article["content"] = await scrape_article(article["url"])
#         # print(f"[RSS] {article['title']}", flush=True)

#     # return {"count": len(articles), "articles":articles}
#     return {
#         "count": len(article),
#         "articles": articles,
#     }
@app.get("/collect/test")
async def collect_test(
    limit: int = Query(default=5, ge=1, le=20, description="수집할 기사 수"),
    ):
    articles = await fetch_news(limit=limit)

    results = []

    for article in articles:
        article["content"] = await scrape_article(article["url"])
        results.append(normalize_article(article))

    return {
        "count": len(results),
        "articles": results,
    }

@app.post("/collect/send-test")
async def collect_send_test():
    articles = await fetch_news(limit=1)
    
    if not articles:
        return {
            "status": "empty",
            "message": "수집된 뉴스가 없습니다.",
        }
    
    article = articles[0]
    article["content"] = await scrape_article(article["url"])

    normalized = normalize_article(article)
    response = await send_article(normalized)

    return {
        "status": "sent",
        "agent_response": response,
    }