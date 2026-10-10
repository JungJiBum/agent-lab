from fastapi import FastAPI, HTTPException
from app.tools.host import get_host_status
from app.tools.container import get_container_status
from app.tools.container import (get_container_status, get_container_details, get_container_logs)

import subprocess

app = FastAPI(title="Host Metrics")


@app.get("/status")
def status():
    return get_host_status()


@app.get("/containers")
def containers():
    return get_container_status()

@app.get("/containers/{container_id}/details")
def container_details(container_id: str):
    try:
        return get_container_details(container_id)
    except subprocess.CalledProcessError:
        raise HTTPException(
            status_code=404,
            detail="Container not found or inaccessible",
        )


@app.get("/containers/{container_id}/logs")
def container_logs(container_id: str, tail: int = 100):
    try:
        return get_container_logs(container_id, tail)
    except subprocess.CalledProcessError:
        raise HTTPException(
            status_code=404,
            detail="Container not found or inaccessible",
        )