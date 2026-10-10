import json
import subprocess


def get_container_status() -> list[dict]:
    result = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )

    containers = []

    for line in result.stdout.splitlines():
        data = json.loads(line)

        containers.append({
            "name": data["Name"],
            "cpu_percent": data["CPUPerc"],
            "memory_usage": data["MemUsage"],
            "memory_percent": data["MemPerc"],
        })

    return containers

def get_container_details(container_id: str) -> dict:
    result = subprocess.run(
        ["docker", "inspect", container_id],
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )

    data = json.loads(result.stdout)[0]
    state = data["State"]

    return {
        "name": data["Name"].lstrip("/"),
        "status": state["Status"],
        "running": state["Running"],
        "restart_count": data["RestartCount"],
        "oom_killed": state["OOMKilled"],
        "exit_code": state["ExitCode"],
        "started_at": state["StartedAt"],
        "finished_at": state["FinishedAt"],
    }

def get_container_logs(
    container_id: str,
    tail: int = 100,
) -> dict:
    tail = max(1, min(tail, 200))

    result = subprocess.run(
        [
            "docker", "logs",
            "--tail", str(tail),
            container_id,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )

    return {
        "container_id": container_id,
        "tail": tail,
        "logs": (result.stdout + result.stderr)[-20000:],
    }