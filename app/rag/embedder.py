import httpx

from app.rag.chunker import chunk_documents

OLLAMA_URL = "http://ollama:11434"


def embed_text(text: str) -> list[float]:
    response = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": "embeddinggemma",
            "input": text
        },
        timeout=60.0
    )

    response.raise_for_status()
    data = response.json()

    return data["embeddings"][0]


def embed_documents(chunks: list[dict] | None = None) -> list[dict]:
    if chunks is None:
        chunks = chunk_documents()

    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["content"])

    return chunks