from app.rag.obsidian_loader import load_documents


def split_text(text: str, chunk_size: int = 500) -> list[str]:
    return [
        text[start:start + chunk_size]
        for start in range(0, len(text), chunk_size)
    ]


def chunk_text_documents(documents: list[dict]) -> list[dict]:
    all_chunks = []

    for doc in documents:
        chunks = split_text(doc["content"])

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                **doc,
                "chunk_index": index,
                "content": chunk,
            })

    return all_chunks


def chunk_documents():
    return chunk_text_documents(load_documents())