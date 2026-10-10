from fastapi import FastAPI
from fastapi.responses import FileResponse

from pydantic import BaseModel
from pathlib import Path
from app.providers import get_llm_provider

app = FastAPI(title="Agent Lab")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def index():
    return FileResponse(
        Path(__file__).parent / "static" / "index.html"
    )

@app.get("/health")
def health():
    return {"status":"OK"}


@app.post("/chat")
async def chat(request: ChatRequest):
    provider = get_llm_provider()
    answer = await provider.chat(request.message)

    return {"answer": answer}