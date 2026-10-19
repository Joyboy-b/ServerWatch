from fastapi import FastAPI, HTTPException

from app.models import Server
from app.monitor import ServerMonitor

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