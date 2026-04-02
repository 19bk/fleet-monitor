from datetime import datetime

from fleet_monitor.simulator.device import DeviceDefinition, DeviceSimulator


def test_device_simulator_generates_bounded_reading() -> None:
    device = DeviceSimulator(
        definition=DeviceDefinition(
            device_id="dev_test",
            name="Test Device",
            device_type="pump",
            county="Nairobi",
            site="CBD",
            latitude=0.0,
            longitude=0.0,
            install_date="2024-01-01",
            last_maintenance_days=15,
            baseline_risk=0.1,
            failure_mode="healthy",
        )
    )

    reading = device.step(datetime(2026, 1, 1, 12, 0, 0))
    assert 0.0 <= reading.health_score <= 1.0
    assert 0.0 <= reading.failure_probability <= 1.0
    assert reading.temperature >= 20.0

