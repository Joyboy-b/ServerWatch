import psutil
from app.config import (
    CPU_THRESHOLD,
    MEMORY_THRESHOLD,
    DISK_THRESHOLD
)

def get_system_metrics(cpu_interval=None):
    cpu = psutil.cpu_percent(interval=cpu_interval)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("/")

    total_gb = round(memory.total / (1 << 30), 2)

    available_gb = round(memory.available / (1 << 30), 2)

    return {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_total_gb": total_gb,
        "memory_available_gb": available_gb,
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