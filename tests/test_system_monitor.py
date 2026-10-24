from unittest.mock import patch, MagicMock
import psutil
import pytest

from app.system_monitor import (
    get_system_metrics,
    evaluate_system_health,
    get_top_processes,
    get_process_by_pid,
    get_top_cpu_processes
)



@patch("app.system_monitor.psutil.Process")
def test_process_access_denied(mock_process_class):
    mock_process_class.side_effect = psutil.AccessDenied(
        pid=1234
    )

    with pytest.raises(psutil.AccessDenied):
        get_process_by_pid(1234)

@patch("app.system_monitor.psutil.Process")
def test_process_not_found(mock_process_class):
    mock_process_class.side_effect = psutil.NoSuchProcess(
        pid=999999
    )

    with pytest.raises(psutil.NoSuchProcess):
        get_process_by_pid(999999)

@patch("app.system_monitor.psutil.Process")
def test_get_process_by_pid(mock_process_class):
    mock_process = MagicMock()

    mock_process.pid = 4321
    mock_process.name.return_value = "python3"
    mock_process.status.return_value = "running"
    mock_process.cpu_percent.return_value = 12.5
    mock_process.memory_info.return_value.rss = (
        128 * (1024 ** 2)
    )

    mock_process_class.return_value = mock_process

    result = get_process_by_pid(4321)

    assert result == {
        "pid": 4321,
        "name": "python3",
        "status": "running",
        "cpu_percent": 12.5,
        "memory_mb": 128.0
    }

    mock_process_class.assert_called_once_with(4321)
    mock_process.cpu_percent.assert_called_once_with(
        interval=0.1
    )

@patch("app.system_monitor.psutil.disk_usage")
@patch("app.system_monitor.psutil.virtual_memory")
@patch("app.system_monitor.psutil.cpu_percent")
def test_memory_used_gb(mock_cpu, mock_memory, mock_disk):
    mock_cpu.return_value = 10.0

    mock_memory.return_value = MagicMock(
        total=16 * (1024 ** 3),
        available=6 * (1024 ** 3),
        used=9 * (1024 ** 3),
        percent=60.0
    )

    mock_disk.return_value = MagicMock(percent=20.0)

    result = get_system_metrics()

    assert result["memory_total_gb"] == 16.0
    assert result["memory_available_gb"] == 6.0
    assert result["memory_used_gb"] == 9.0

    mock_memory.assert_called_once_with()

@patch("app.system_monitor.psutil.disk_usage")
@patch("app.system_monitor.psutil.virtual_memory")
@patch("app.system_monitor.psutil.cpu_percent")
def test_memory_conversion(mock_cpu, mock_memory, mock_disk):
    mock_cpu.return_value = 20.0
    mock_memory.return_value = MagicMock(
        total=8 * (1024 ** 3),
        available=4 * (1024 ** 3),
        percent=50.0
    )

    mock_disk.return_value = MagicMock(percent=30.0)

    result = get_system_metrics()

    assert result["memory_total_gb"] == 8.0
    assert result["memory_available_gb"] == 4.0
    assert result["memory_percent"] == 50.0

    mock_memory.assert_called_once_with()

@patch("app.system_monitor.psutil.disk_usage")
@patch("app.system_monitor.psutil.virtual_memory")
@patch("app.system_monitor.psutil.cpu_percent")
def test_memory_rounding(mock_cpu, mock_memory, mock_disk):
    mock_cpu.return_value = 10.0

    mock_memory.return_value = MagicMock(
        total=int(7.7567 * (1024 ** 3)),
        available=int(3.4567 * (1024 ** 3)),
        percent=55.4
    )

    mock_disk.return_value = MagicMock(percent=20.0)

    result = get_system_metrics()

    assert result["memory_total_gb"] == 7.76
    assert result["memory_available_gb"] == 3.46


@patch("app.system_monitor.psutil.disk_usage")
@patch("app.system_monitor.psutil.virtual_memory")
@patch("app.system_monitor.psutil.cpu_percent")
def test_get_system_metrics(mock_cpu, mock_memory, mock_disk):
    mock_cpu.return_value = 95.0

    mock_memory.return_value = MagicMock(
        total=16 * (1024 ** 3),
        available=8 * (1024 ** 3),
        used=9 * (1024 ** 3),
        percent=70.0
    )

    mock_disk.return_value = MagicMock(percent=40.0)

    result = get_system_metrics()

    assert result == {
        "cpu_percent": 95.0,
        "memory_percent": 70.0,
        "memory_total_gb": 16.0,
        "memory_available_gb": 8.0,
        "memory_used_gb": 9.0,
        "disk_percent": 40.0
    }

    mock_cpu.assert_called_once_with(interval=None)
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



@patch("app.system_monitor.psutil.process_iter")
def test_top_cpu_processes(mock_iter):
    p1 = MagicMock()
    p1.info = {
        "pid": 101,
        "name": "python",
        "cpu_percent": 75.0
    }

    p2 = MagicMock()
    p2.info = {
        "pid": 102,
        "name": "nginx",
        "cpu_percent": 20.0
    }

    p3 = MagicMock()
    p3.info = {
        "pid": 103,
        "name": "postgres",
        "cpu_percent": 90.0
    }

    mock_iter.return_value = [p1, p2, p3]

    result = get_top_cpu_processes(2)

    assert len(result) == 2
    assert result[0]["pid"] == 103
    assert result[1]["pid"] == 101
