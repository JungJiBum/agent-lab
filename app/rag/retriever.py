from app.rag.embedder import embed_text
from app.rag.vector_store import collection


def search_documents(query: str):
    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return results
