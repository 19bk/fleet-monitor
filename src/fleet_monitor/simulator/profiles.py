"""Failure profiles used by the simulator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureProfile:
    name: str
    label: str
    degradation_rate: float
    temperature_bias: float
    vibration_bias: float
    rpm_bias: float
    torque_bias: float
    power_bias: float
    wear_bias: float
    flow_bias: float
    pressure_bias: float


FAILURE_PROFILES: dict[str, FailureProfile] = {
    "healthy": FailureProfile(
        name="healthy",
        label="Normal operation",
        degradation_rate=0.0003,
        temperature_bias=0.0,
        vibration_bias=0.0,
        rpm_bias=0.0,
        torque_bias=0.0,
        power_bias=0.0,
        wear_bias=0.0,
        flow_bias=0.0,
        pressure_bias=0.0,
    ),
    "twf": FailureProfile(
        name="twf",
        label="Tool wear failure",
        degradation_rate=0.0017,
        temperature_bias=2.0,
        vibration_bias=0.7,
        rpm_bias=-35.0,
        torque_bias=1.4,
        power_bias=18.0,
        wear_bias=6.5,
        flow_bias=-0.3,
        pressure_bias=-0.05,
    ),
    "hdf": FailureProfile(
        name="hdf",
        label="Heat dissipation failure",
        degradation_rate=0.0023,
        temperature_bias=8.5,
        vibration_bias=0.4,
        rpm_bias=-20.0,
        torque_bias=0.8,
        power_bias=25.0,
        wear_bias=1.0,
        flow_bias=-0.2,
        pressure_bias=-0.1,
    ),
    "pwf": FailureProfile(
        name="pwf",
        label="Power failure",
        degradation_rate=0.0019,
        temperature_bias=3.0,
        vibration_bias=0.5,
        rpm_bias=-90.0,
        torque_bias=3.0,
        power_bias=40.0,
        wear_bias=2.5,
        flow_bias=-0.5,
        pressure_bias=-0.2,
    ),
    "osf": FailureProfile(
        name="osf",
        label="Overstrain failure",
        degradation_rate=0.0021,
        temperature_bias=4.5,
        vibration_bias=1.2,
        rpm_bias=25.0,
        torque_bias=6.0,
        power_bias=30.0,
        wear_bias=4.0,
        flow_bias=-0.4,
        pressure_bias=-0.15,
    ),
    "rnf": FailureProfile(
        name="rnf",
        label="Random failure",
        degradation_rate=0.0027,
        temperature_bias=1.5,
        vibration_bias=1.7,
        rpm_bias=-10.0,
        torque_bias=2.2,
        power_bias=15.0,
        wear_bias=3.0,
        flow_bias=-0.2,
        pressure_bias=-0.1,
    ),
}

