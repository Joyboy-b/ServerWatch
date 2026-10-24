import socket
import time

def check_tcp_service(
    host: str,
    port: int,
    timeout: float = 2.0
) -> dict:

    start = time.monotonic()

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout
        ):
            latency_ms = round(
                (time.monotonic() - start) * 1000, 2
            )

            return {
                "host": host,
                "port": port,
                "status": "UP",
                "latency_ms": latency_ms,
                "error": None
            }
    except (OSError, TimeoutError) as exc:
        return {
            "host": host,
            "port": port, 
            "status": "DOWN",
            "latency_ms": None,
            "error": str(exc)
        }