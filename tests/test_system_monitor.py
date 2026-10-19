from unittest.mock import patch, MagicMock

from app.system_monitor import (
    get_system_metrics,
    evaluate_system_health,
    get_top_processes
)

@patch("app.system_monitor.psutil.disk_usage")
@patch("app.system_monitor.psutil.virtual_memory")
@patch("app.system_monitor.psutil.cpu_percent")
def test_get_system_metrics(mock_cpu, mock_memory, mock_disk):
    mock_cpu.return_value = 95.0

    mock_memory.return_value = MagicMock(percent=70.0)

    mock_disk.return_value = MagicMock(percent=40.0)

    result = get_system_metrics()

    assert result == {
        "cpu_percent": 95.0,
        "memory_percent": 70.0,
        "disk_percent": 40.0
    }

    mock_cpu.assert_called_once_with(interval=1)
    mock_disk.assert_called_once_with("/")

def test_healthy_system():
    metrics = {
        "cpu_percent": 40, 
        "memory_percent": 50,
        "disk_percent": 30
    }

    result = evaluate_system_health(metrics)

    assert result["status"] == "HEALTHY"
    assert result["reasons"] == []

def test_high_cpu_system():
    metrics = {
        "cpu_percent": 95,
        "memory_percent": 50,
        "disk_percent": 30
    }

    result = evaluate_system_health(metrics)

    assert result["status"] == "UNHEALTHY"
    assert "High CPU" in result["reasons"]

def test_multiple_resource_failures():
    metrics = {
        "cpu_percent": 99,
        "memory_percent": 95,
        "disk_percent": 98
    }

    result = evaluate_system_health(metrics)

    assert result["status"] == "UNHEALTHY"
    assert len(result["reasons"]) == 3

@patch("app.system_monitor.psutil.process_iter")
def test_top_processes(mock_process_iter):
    def fake_process(pid, name, memory):
        process = MagicMock()
        process.info = {
            "pid": pid,
            "name": name,
            "cpu_percent": 0.0,
            "memory_percent": memory
        }
        return process
    mock_process_iter.return_value = [
        fake_process(101, "python", 10.0),
        fake_process(102, "nginx", 25.0),
        fake_process(103, "redis", 15.0)
    ]
    
    result = get_top_processes(limit=2)

    assert len(result) == 2
    assert result[0]["name"] == "nginx"
    assert result[1]["name"] == "redis"