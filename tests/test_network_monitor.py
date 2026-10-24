from unittest.mock import patch, MagicMock

from app.network_monitor import check_tcp_service

@patch("app.network_monitor.socket.create_connection")
def test_tcp_service_up(mock_connection):
    mock_connection.return_value = MagicMock()

    result = check_tcp_service("127.0.0.1", 8000)

    assert result["status"] == "UP"
    assert result["error"] is None
    assert result["latency_ms"] >= 0

    mock_connection.assert_called_once_with(
        ("127.0.0.1", 8000),
        timeout=2.0
    )

@patch("app.network_monitor.socket.create_connection")
def test_tcp_service_down(mock_connection):
    mock_connection.side_effect = ConnectionRefusedError(
        "Connection refused"
    )

    result = check_tcp_service("127.0.0.1", 8000)

    assert result["status"] = "DOWN"
    assert result["latency_ms"] is None
    assert "Connection refused" in result["error"]

@patch("app.network_monitor.socket.create_connection")
def test_tcp_timeout(mock_connection):
    mock_connection.side_effect = TimeoutError(
        "Connection timed out"
    )

    result = check_tcp_service(
        "127.0.0.1",
        8000,
        timeout=0.5
    )

    assert result["status"] == "DOWN"
    assert "timed out" in result["error"]