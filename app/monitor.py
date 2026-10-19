from app.models import Server 
from app.config import CPU_THRESHOLD, MEMORY_THRESHOLD

class ServerMonitor:
    def __init__(self):
        self.servers: dict[str, Server] = {}

    def add_server(self, server: Server):
        self.servers[server.id] = server 

    def check_health(self, server: Server):
        reasons = []

        if not server.online:
            reasons.append("Offline")

        if server.cpu > CPU_THRESHOLD:
            reasons.append("High CPU")

        if server.memory > MEMORY_THRESHOLD:
            reasons.append("High Memory")

        if reasons:
            return {
                "status": "UNHEALTHY",
                "reasons": reasons
            }

        return {
            "status": "HEALTHY",
            "reasons": []
        }

    def get_unhealthy_servers(self):
        unhealthy = {}

        for server_id, server in self.servers.items():
            result = self.check_health(server)

            if result["status"] == "UNHEALTHY":
                unhealthy[server_id] = result["reasons"]

        return unhealthy