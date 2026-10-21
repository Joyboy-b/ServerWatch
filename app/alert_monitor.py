from collections import deque

class CPUAlertMonitor:
    def __init__(
        self,
        threshold: float = 85.0,
        consecutive: int = 3
    ):
        if consecutive < 1:
            raise ValueError("consecutive must be positive")

        self.threshold = threshold
        self.consecutive = consecutive

        self.history = deque(maxlen=consecutive)

    def record(self, cpu_percent: float) -> bool:
        is_high = cpu_percent >= self.threshold

        self.history.append(is_high)

        if len(self.history) < self.consecutive:
            return False

        return all(self.history)

