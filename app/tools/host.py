import psutil


def get_host_status() -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_total_gb": round(
            psutil.virtual_memory().total / (1024 ** 3), 2
        ),
    }