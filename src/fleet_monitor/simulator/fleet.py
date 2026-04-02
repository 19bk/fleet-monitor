"""Fleet simulator orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path

from fleet_monitor.simulator.device import DeviceDefinition, DeviceSimulator, TelemetryReading


@dataclass
class FleetSimulator:
    devices: list[DeviceSimulator]

    @classmethod
    def from_config(cls, config_path: str | Path) -> "FleetSimulator":
        with open(config_path, encoding="utf-8") as handle:
            payload = json.load(handle)
        devices = [
            DeviceSimulator(definition=DeviceDefinition(**device), seed=index + 7)
            for index, device in enumerate(payload["devices"])
        ]
        return cls(devices=devices)

    def tick(self, timestamp: datetime | None = None, interval_minutes: int = 60) -> list[TelemetryReading]:
        now = timestamp or datetime.utcnow()
        return [device.step(now, interval_minutes=interval_minutes) for device in self.devices]

    def generate_history(
        self,
        days: int,
        interval_minutes: int = 60,
        end_time: datetime | None = None,
    ) -> list[TelemetryReading]:
        readings: list[TelemetryReading] = []
        end = end_time or datetime.utcnow()
        periods = int((days * 24 * 60) / interval_minutes)
        start = end - timedelta(minutes=periods * interval_minutes)
        current = start
        for _ in range(periods):
            readings.extend(self.tick(timestamp=current, interval_minutes=interval_minutes))
            current += timedelta(minutes=interval_minutes)
        return readings

