import psutil
import heapq
from app.config import (
    CPU_THRESHOLD,
    MEMORY_THRESHOLD,
    DISK_THRESHOLD
)

def get_top_cpu_processes(k: int = 5) -> list[dict]:
    if k < 1:
        raise ValueError("k must be positive")

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent"]
    ):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": info["cpu_percent"] or 0.0
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied.
            psutil.ZombieProcess
        ):
            continue

    return heapq.nlargest(
        k,
        processes,
        key=lambda p: (
            p["cpu_percent"],
            -p["pid"]
        )
    )

def get_system_metrics(cpu_interval=None):
    cpu = psutil.cpu_percent(interval=cpu_interval)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("/")

    total_gb = round(memory.total / (1 << 30), 2)

    available_gb = round(memory.available / (1 << 30), 2)

    used_gb = round(memory.used / (1 << 30), 2)

    return {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_total_gb": total_gb,
        "memory_available_gb": available_gb,
        "memory_used_gb": used_gb,
        "disk_percent": disk.percent
    }

if __name__ == "__main__":
    print(get_system_metrics(cpu_interval=1))

def evaluate_system_health(metrics):
    reasons = []

    if metrics["cpu_percent"] > CPU_THRESHOLD:
        reasons.append("High CPU")

    if metrics["memory_percent"] > MEMORY_THRESHOLD:
        reasons.append("High Memory")

    if metrics["disk_percent"] > DISK_THRESHOLD:
        reasons.append("High Disk Usage")

    return {
        "status": "UNHEALTHY" if reasons else "HEALTHY",
        "reasons": reasons
    }

def get_top_processes(limit=5):
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            info = proc.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": info["cpu_percent"] or 0.0,
                "memory_percent": info["memory_percent"] or 0.0
            })
        
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue
    processes.sort(
        key=lambda process: process["memory_percent"],
        reverse=True
    )

    return processes[:limit]

def get_process_by_pid(pid: int) -> dict:
    try:
        process = psutil.Process(pid)

        memory_bytes = process.memory_info().rss

        memory_mb = round(
            memory_bytes / (1024 ** 2), 2
        )

        return {
            "pid": process.pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": memory_mb
        }

    except psutil.NoSuchProcess:
        raise

    except psutil.AccessDenied:
        raise
