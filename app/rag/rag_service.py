from app.rag.retriever import search_documents
import httpx


def ask_rag(question: str):
    results = search_documents(question)

    context = "\n\n".join(results["documents"][0])

    prompt = f"""
다음 참고 문서를 바탕으로 질문에 답변하세요.
참고 문서에 답이 없다면 모른다고 답변하세요.

[참고 문서]
{context}

[질문]
{question}
"""

    response = httpx.post(
        "http://ollama:11434/api/chat",
        json={
            "model": "qwen3:8b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        },
        timeout=120.0
    )
    
    response.raise_for_status()
    return response.json()["message"]["content"]