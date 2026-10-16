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

def embed_documents():
    chunks = chunk_documents()

    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["content"])

    return chunks

if __name__ == "__main__":
    documents = embed_documents()

    print(f"전체 임베딩 수: {len(documents)}")
    print(f"첫 번째 문서: {documents[0]['path']}")
    print(f"벡터 차원: {len(documents[0]['embedding'])}")