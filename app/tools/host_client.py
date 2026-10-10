import httpx

METRICS_URL = "http://host.docker.internal:8001"


async def get_host_status_remote() -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{METRICS_URL}/status")
        response.raise_for_status()
        return response.json()


async def get_container_status_remote() -> list[dict]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(f"{METRICS_URL}/containers")
        response.raise_for_status()
        return response.json()