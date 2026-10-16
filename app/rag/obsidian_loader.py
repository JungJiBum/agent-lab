from pathlib import Path

def load_documents():
    vault = Path("/data/obsidian")
    files = list(vault.rglob("*.md"))
    documents = []

    for file in files:
        content = file.read_text(encoding="utf-8")
        #read_text -> 파일의 내용을 읽을때 사용

        documents.append({
            "source" : "obsidian",
            "path": str(file.relative_to(vault)), #relative_to -> 상대경로 구할때 사용
            "content": content
        })
    return documents