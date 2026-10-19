import pytest

from app.models import Server
from app.monitor import ServerMonitor

@pytest.fixture
def monitor():
    return ServerMonitor()

def test_add_server(monitor):
    server = Server("s1", 40, 50, True)

    monitor.add_server(server)

    assert "s1" in monitor.servers

def test_healthy_server(monitor):
    server = Server("s1", 40, 50, True)

    result = monitor.check_health(server)

    assert result["status"] == "HEALTHY"

def test_high_cpu(monitor):
    server = Server("s2", 95, 50, True)

    result = monitor.check_health(server)

    assert result["status"] == "UNHEALTHY"
    assert "High CPU" in result["reasons"]

def test_high_memory(monitor):
    server = Server("s3", 40, 95, True)

    result = monitor.check_health(server)

    assert "High Memory" in result["reasons"]

def test_offline_server(monitor):
    server = Server("s4", 20, 30, False)

    result = monitor.check_health(server)

    assert "Offline" in result["reasons"]

def test_multiple_failures(monitor):
    server = Server("s5", 99, 95, False)

    result = monitor.check_health(server)

    assert len(result["reasons"]) == 3

def test_unhealthy_servers(monitor):
    monitor.add_server(Server("s1", 40, 50, True))
    monitor.add_server(Server("s2", 95, 50, True))
    monitor.add_server(Server("s3", 20, 95, True))

    result = monitor.get_unhealthy_servers()

    assert len(result) == 2
    assert "s1" not in result
    assert "s2" in result
    assert "s3" in result

def test_cpu_boundary(monitor):
    server = Server("s1", 85, 50, True)

    result = monitor.check_health(server)

    assert result["status"] == "HEALTHY"