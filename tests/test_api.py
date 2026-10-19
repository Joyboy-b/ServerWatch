from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_homem():
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

