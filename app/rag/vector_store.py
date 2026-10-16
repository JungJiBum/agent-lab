import chromadb
from app.rag.embedder import embed_documents

client = chromadb.PersistentClient(path="/app/data/chroma")

collection = client.get_or_create_collection(
    name="obsidian"
)


def save_documents():
    documents = embed_documents()
    for doc in documents:
        collection.upsert(
            ids=[f"{doc['source']}:{doc['path']}:{doc['chunk_index']}"],
            documents=[doc["content"]],
            embeddings=[doc["embedding"]],
            metadatas=[{"source": doc["source"],"path": doc["path"],"chunk_index": doc["chunk_index"]}]
        )



if __name__ == "__main__":
    save_documents()
    print(f"컬렉션 이름: {collection.name}")
    print(f"저장된 데이터 수: {collection.count()}")
