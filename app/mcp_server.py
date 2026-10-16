import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import quote
from app.rag.retriever  import search_documents

mcp = FastMCP("Agent Lab Metrics")

METRICS_URL = "http://host.docker.internal:8001"

@mcp.tool()
async def get_container_details(container_id: str) -> dict:
    """지정한 Docker 컨테이너의 실행 상태, 재시작 횟수,
    OOM 여부와 종료 코드를 조회합니다."""
    container_id = quote(container_id, safe="")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{METRICS_URL}/containers/{container_id}/details"
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_container_logs(
    container_id: str,
    tail: int = 100,
) -> dict:
    """지정한 Docker 컨테이너의 최근 로그를 조회합니다.
    장애 원인 분석에 활용합니다."""
    container_id = quote(container_id, safe="")
    tail = max(1, min(tail, 200))

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{METRICS_URL}/containers/{container_id}/logs",
            params={"tail": tail},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_host_status() -> dict:
    """Mac mini 호스트의 CPU와 메모리 상태를 조회합니다."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{METRICS_URL}/status")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_container_status() -> list[dict]:
    """실행 중인 Docker 컨테이너의 CPU와 메모리 상태를 조회합니다."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(f"{METRICS_URL}/containers")
        response.raise_for_status()
        return response.json()

@mcp.tool()
def search_obsidian(query: str) -> list[dict]:
    """Obsidian 문서에서 질문과 관련된 내용을 검색합니다."""
    results = search_documents(query)

    return [
        {
            "content": content,
            "source": metadata["source"],
            "path": metadata["path"],
        }
        for content, metadata in zip(
            results["documents"][0],
            results["metadatas"][0],
        )
    ]

if __name__ == "__main__":
    mcp.run(transport="stdio")