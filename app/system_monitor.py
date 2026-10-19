import psutil
from app.config import (
    CPU_THRESHOLD,
    MEMORY_THRESHOLD,
    DISK_THRESHOLD
)

def get_system_metrics():
    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("/")

    return {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent
    }

if __name__ == "__main__":
    print(get_system_metrics())

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