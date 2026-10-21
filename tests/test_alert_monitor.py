from app.alert_monitor import CPUAlertMonitor


def test_three_consecutive_failures():
    monitor = CPUAlertMonitor()

    assert monitor.record(90) is False
    assert monitor.record(92) is False
    assert monitor.record(95) is True


def test_normal_reading_resets_streak():
    monitor = CPUAlertMonitor()

    monitor.record(90)
    monitor.record(92)
    monitor.record(40)

    assert monitor.record(95) is False


def test_threshold_boundary():
    monitor = CPUAlertMonitor(threshold=85)

    monitor.record(85)
    monitor.record(85)

    assert monitor.record(85) is True
