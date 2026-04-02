from datetime import datetime

from fleet_monitor.simulator.device import TelemetryReading
from fleet_monitor.storage.store import FleetStore


def test_store_round_trip(tmp_path) -> None:
    store = FleetStore(tmp_path / "fleet.db")
    store.initialize()
    inserted = store.insert_readings(
        [
            TelemetryReading(
                timestamp=datetime(2026, 1, 1, 12, 0, 0),
                device_id="dev_001",
                health_score=0.72,
                failure_probability=0.23,
                predicted_failure_mode="healthy",
                temperature=44.0,
                pressure=3.1,
                vibration=1.9,
                rpm=1500.0,
                torque=40.0,
                power_draw=760.0,
                flow_rate=18.0,
                voltage=231.0,
                tool_wear=48.0,
            )
        ]
    )
    assert inserted == 1
    assert len(store.latest_telemetry()) == 1

