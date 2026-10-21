from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import psutil

client = TestClient(app)

def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "ServerWatch API is running"

def test_get_servers():
    response = client.get("/servers")

    assert response.status_code == 200
    assert len(response.json()) == 4

def test_get_health():
    response = client.get("/servers/health")

    assert response.status_code == 200

    data = response.json()

    assert data["server1"]["status"] == "HEALTHY"
    assert data["server2"]["status"] == "UNHEALTHY"

def test_get_unhealthy():
    response = client.get("/servers/unhealthy")

    assert response.status_code == 200

    data = response.json()

    assert "server1" not in data
    assert "server2" in data

def test_unknown_route():
    response = client.get("/unknown")

    assert response.status_code == 404

def test_get_existing_server():
    response = client.get("/servers/server2")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == "server2"
    assert data["cpu"] == 95
    assert data["status"] == "UNHEALTHY"
    assert "High CPU" in data["reasons"]

def test_get_nonexistent_server():
    response = client.get("/servers/server99")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Server not found"

@patch("app.main.get_system_metrics")
def test_system_metrics_endpoint(mock_metrics):
    mock_metrics.return_value = {
        "cpu_percent": 95.0,
        "memory_percent": 70.0,
        "memory_total_gb": 16.0,
        "memory_available_gb": 8.0,
        "memory_used_gb": 9.0,
        "disk_percent": 40.0
    }

    response = client.get("/system/metrics")

    assert response.status_code == 200

    data = response.json()

    assert data["cpu_percent"] == 95.0
    assert data["memory_percent"] == 70.0
    assert data["memory_total_gb"] == 16.0
    assert data["memory_available_gb"] == 8.0
    assert data["disk_percent"] == 40.0

    mock_metrics.assert_called_once_with()


@patch("app.main.get_top_processes")
def test_process_endpoint(mock_processes):
    mock_processes.return_value = [
        {
            "pid": 101,
            "name": "python",
            "cpu_percent": 0.0,
            "memory_percent": 12.5
        }
    ]

    response = client.get("/system/processes?limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["pid"] == 101
    mock_processes.assert_called_once_with(1)



@patch("app.main.get_process_by_pid")
def test_process_endpoint_success(mock_get_process):
    mock_get_process.return_value = {
        "pid": 4321,
        "name": "python3",
        "status": "running",
        "cpu_percent": 12.5,
        "memory_mb": 128.0
    }

    response = client.get("/system/processes/4321")

    assert response.status_code == 200
    assert response.json()["pid"] == 4321
    assert response.json()["name"] == "python3"

    mock_get_process.assert_called_once_with(4321)


@patch("app.main.get_process_by_pid")
def test_process_endpoint_not_found(mock_get_process):
    mock_get_process.side_effect = psutil.NoSuchProcess(
        pid=999999
    )

    response = client.get("/system/processes/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Process 999999 not found"
    }


@patch("app.main.get_process_by_pid")
def test_process_endpoint_access_denied(mock_get_process):
    mock_get_process.side_effect = psutil.AccessDenied(
        pid=1234
    )

    response = client.get("/system/processes/1234")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Access denied for process 1234"
    }


def test_process_endpoint_invalid_pid():
    response = client.get("/system/processes/0")

    assert response.status_code == 422
