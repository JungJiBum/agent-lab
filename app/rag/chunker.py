from app.rag.obsidian_loader import load_documents

def split_text(text: str, chunk_size: int = 500) -> list[str]:
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)

    return chunks

def chunk_documents():
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        chunks = split_text(doc["content"])

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "path": doc["path"],
                "chunk_index": index,
                "content": chunk
            })

    return all_chunks

if __name__ == "__main__":
    chunks = chunk_documents()
    print(f"전체 청크 수 : {len(chunks)}")