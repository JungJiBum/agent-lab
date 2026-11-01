import hashlib
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from app.rag.chunker import chunk_text_documents
from app.rag.embedder import embed_documents
from app.rag.vector_store import upsert_documents

router = APIRouter(prefix="/api/news", tags=["News"])


class NewsArticle(BaseModel):
    title: str
    url: HttpUrl
    published_at: datetime
    content: str
    source: str
    collected_at: datetime


@router.post("/ingest")
def ingest_news(article: NewsArticle):
    article_data = article.model_dump(mode="json")

    if not article.content.strip():
        return {
            "status": "skipped",
            "message": "기사 본문이 비어 있습니다.",
            "title": article.title,
        }

    # 1. Chunking
    chunks = chunk_text_documents([article_data])

    # 2. Embedding
    embedded_chunks = embed_documents(chunks)

    # 3. ChromaDB 저장 형식으로 변환
    url_hash = hashlib.sha256(
        str(article.url).encode("utf-8")
    ).hexdigest()

    documents = []

    for chunk in embedded_chunks:
        documents.append({
            "id": f"{url_hash}:{chunk['chunk_index']}",
            "content": chunk["content"],
            "embedding": chunk["embedding"],
            "metadata": {
                "title": chunk["title"],
                "url": chunk["url"],
                "source": chunk["source"],
                "published_at": chunk["published_at"],
                "chunk_index": chunk["chunk_index"],
            },
        })

    # 4. ChromaDB 저장
    saved_count = upsert_documents(
        collection_name="ai_news",
        documents=documents,
    )

    return {
        "status": "saved",
        "title": article.title,
        "chunks": saved_count,
        "collection": "ai_news",
    }