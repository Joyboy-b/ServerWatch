from fastapi import FastAPI, HTTPException, Query, Path
import psutil
from app.models import Server
from app.monitor import ServerMonitor

from app.system_monitor import get_system_metrics, evaluate_system_health, get_top_processes,  get_process_by_pid

app = FastAPI(title="ServerWatch API")

monitor = ServerMonitor()

monitor.add_server(Server("server1", 45, 60, True))
monitor.add_server(Server("server2", 95, 70, True))
monitor.add_server(Server("server3", 40, 95, True))
monitor.add_server(Server("server4", 20, 30, False))

@app.get("/")
def home():
    return {"message": "ServerWatch API is running"}

@app.get("/servers")
def get_servers():
    return [
        {
            "id": server.id,
            "cpu": server.cpu,
            "memory": server.memory,
            "online": server.online
        }
        for server in monitor.servers.values()
    ]

@app.get("/servers/health")
def get_health():
    results = {}

    for server_id, server in monitor.servers.items():
        results[server_id] = monitor.check_health(server)

    return results

@app.get("/servers/unhealthy")
def get_unhealthy():
    return monitor.get_unhealthy_servers()

@app.get("/system/metrics")
def system_metrics():
    return get_system_metrics()

@app.get("/system/health")
def system_health():
    metrics = get_system_metrics()

    health = evaluate_system_health(metrics)

    return {
        "metrics": metrics,
        "status": health["status"],
        "reasons": health["reasons"]
    }

@app.get("/system/processes")
def top_processes(
    limit: int = Query(default=5, ge=1, le=100)
):
    return get_top_processes(limit)

@app.get("/servers/{server_id}")
def get_server(server_id: str):

    if server_id not in monitor.servers:
        raise HTTPException(
            status_code=404,
            detail="Server not found"
        )

    server = monitor.servers[server_id]

    result = monitor.check_health(server)

    return {
        "id": server.id,
        "cpu": server.cpu,
        "memory": server.memory,
        "online": server.online,
        "status": result["status"],
        "reasons": result["reasons"]
    }

@app.get("/system/processes/{pid}")
def get_process_endpoint(pid: int = Path(ge=1)):
    try:
        return get_process_by_pid(pid)

    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=404,
            detail=f"Process {pid} not found"
        )

    except psutil.AccessDenied:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied for process {pid}"
        )
