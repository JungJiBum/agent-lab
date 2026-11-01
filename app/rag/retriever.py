from app.rag.embedder import embed_text
from app.rag.vector_store import client


def search_documents(
    query: str,
    collection_name: str = "obsidian",
    n_results: int = 3,
):
    query_embedding = embed_text(query)

    collection = client.get_or_create_collection(
        name=collection_name
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results