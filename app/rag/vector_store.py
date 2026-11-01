import chromadb
from app.rag.embedder import embed_documents

client = chromadb.PersistentClient(path="/app/data/chroma")


def upsert_documents(
    collection_name: str,
    documents: list[dict],
) -> int:
    if not documents:
        return 0

    collection = client.get_or_create_collection(
        name=collection_name
    )

    collection.upsert(
        ids=[doc["id"] for doc in documents],
        documents=[doc["content"] for doc in documents],
        embeddings=[doc["embedding"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents],
    )

    return len(documents)

def save_documents():
    documents = embed_documents()

    obsidian_documents = []

    for doc in documents:
        obsidian_documents.append({
            "id": f"{doc['source']}:{doc['path']}:{doc['chunk_index']}",
            "content": doc["content"],
            "embedding": doc["embedding"],
            "metadata": {
                "source": doc["source"],
                "path": doc["path"],
                "chunk_index": doc["chunk_index"],
            },
        })

    return upsert_documents(
        collection_name="obsidian",
        documents=obsidian_documents,
    )
