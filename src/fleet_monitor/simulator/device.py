"""Device simulation primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import random

from fleet_monitor.simulator.profiles import FAILURE_PROFILES, FailureProfile


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass
class DeviceDefinition:
    device_id: str
    name: str
    device_type: str
    county: str
    site: str
    latitude: float
    longitude: float
    install_date: str
    last_maintenance_days: int
    baseline_risk: float
    failure_mode: str


@dataclass
class TelemetryReading:
    timestamp: datetime
    device_id: str
    health_score: float
    failure_probability: float
    predicted_failure_mode: str
    temperature: float
    pressure: float
    vibration: float
    rpm: float
    torque: float
    power_draw: float
    flow_rate: float
    voltage: float
    tool_wear: float

    def as_record(self) -> dict[str, object]:
        record = asdict(self)
        record["timestamp"] = self.timestamp.isoformat()
        return record


@dataclass
class DeviceSimulator:
    definition: DeviceDefinition
    seed: int = 42
    health: float = 1.0
    tool_wear: float = 0.0
    cumulative_runtime_hours: float = 0.0
    random_state: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.random_state = random.Random(f"{self.seed}-{self.definition.device_id}")
        self.health = _clamp(1.0 - self.definition.baseline_risk, 0.2, 0.99)
        self.tool_wear = self.definition.last_maintenance_days * 2.1

    @property
    def profile(self) -> FailureProfile:
        return FAILURE_PROFILES.get(self.definition.failure_mode, FAILURE_PROFILES["healthy"])

    def step(self, timestamp: datetime, interval_minutes: int = 60) -> TelemetryReading:
        degradation = self._advance_health(interval_minutes)
        sensor = self._generate_sensor_values(degradation)
        return TelemetryReading(
            timestamp=timestamp,
            device_id=self.definition.device_id,
            health_score=sensor["health_score"],
            failure_probability=sensor["failure_probability"],
            predicted_failure_mode=self.profile.name,
            temperature=sensor["temperature"],
            pressure=sensor["pressure"],
            vibration=sensor["vibration"],
            rpm=sensor["rpm"],
            torque=sensor["torque"],
            power_draw=sensor["power_draw"],
            flow_rate=sensor["flow_rate"],
            voltage=sensor["voltage"],
            tool_wear=sensor["tool_wear"],
        )

    def _advance_health(self, interval_minutes: int) -> float:
        hours = interval_minutes / 60.0
        self.cumulative_runtime_hours += hours
        profile = self.profile
        degradation = profile.degradation_rate * hours
        stochastic = self.random_state.uniform(0.0, 0.0009)
        self.health = _clamp(self.health - degradation - stochastic, 0.02, 0.99)
        self.tool_wear = _clamp(self.tool_wear + profile.wear_bias * hours + self.random_state.uniform(0, 3), 0, 400)
        return 1.0 - self.health

    def _drift(self, current: float, spread: float, lower: float, upper: float) -> float:
        value = current + self.random_state.uniform(-spread, spread)
        return _clamp(value, lower, upper)

    def _generate_sensor_values(self, degradation: float) -> dict[str, float | str]:
        profile = self.profile
        temperature = self._drift(42.0 + degradation * 36.0 + profile.temperature_bias, 1.8, 20.0, 120.0)
        pressure = self._drift(3.2 - degradation * 1.5 + profile.pressure_bias, 0.12, 0.5, 6.0)
        vibration = self._drift(1.6 + degradation * 6.5 + profile.vibration_bias, 0.25, 0.2, 15.0)
        rpm = self._drift(1500.0 - degradation * 260.0 + profile.rpm_bias, 40.0, 500.0, 2200.0)
        torque = self._drift(42.0 + degradation * 11.0 + profile.torque_bias, 1.1, 5.0, 90.0)
        power_draw = self._drift(760.0 + degradation * 320.0 + profile.power_bias, 12.0, 200.0, 2000.0)
        flow_rate = self._drift(18.0 - degradation * 7.0 + profile.flow_bias, 0.4, 0.0, 35.0)
        voltage = self._drift(231.0 - degradation * 12.0, 1.7, 180.0, 260.0)
        tool_wear = self._drift(self.tool_wear, 2.5, 0.0, 420.0)

        health_score = _clamp(
            1.0
            - (max(0.0, vibration - 2.5) / 10.0) * 0.25
            - (max(0.0, temperature - 65.0) / 55.0) * 0.2
            - (max(0.0, 2.2 - pressure) / 2.2) * 0.15
            - (max(0.0, 14.0 - flow_rate) / 14.0) * 0.15
            - (max(0.0, tool_wear - 180.0) / 220.0) * 0.1
            - (max(0.0, power_draw - 980.0) / 1020.0) * 0.15,
            0.0,
            1.0,
        )

        failure_probability = _clamp(
            (1.0 - health_score) * 0.75 + degradation * 0.35 + self.definition.baseline_risk * 0.4,
            0.01,
            0.995,
        )

        return {
            "temperature": round(temperature, 3),
            "pressure": round(pressure, 3),
            "vibration": round(vibration, 3),
            "rpm": round(rpm, 3),
            "torque": round(torque, 3),
            "power_draw": round(power_draw, 3),
            "flow_rate": round(flow_rate, 3),
            "voltage": round(voltage, 3),
            "tool_wear": round(tool_wear, 3),
            "health_score": round(health_score, 4),
            "failure_probability": round(failure_probability, 4),
        }

