"""SQLite storage for telemetry, alerts, and model artifacts."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import sqlite3
from pathlib import Path

from fleet_monitor.simulator.device import TelemetryReading


@dataclass
class AlertRecord:
    timestamp: str
    device_id: str
    severity: str
    title: str
    message: str
    predicted_failure_mode: str
    health_score: float
    failure_probability: float


class FleetStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS telemetry (
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    health_score REAL NOT NULL,
                    failure_probability REAL NOT NULL,
                    predicted_failure_mode TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    pressure REAL NOT NULL,
                    vibration REAL NOT NULL,
                    rpm REAL NOT NULL,
                    torque REAL NOT NULL,
                    power_draw REAL NOT NULL,
                    flow_rate REAL NOT NULL,
                    voltage REAL NOT NULL,
                    tool_wear REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_telemetry_device_time
                ON telemetry (device_id, timestamp);

                CREATE TABLE IF NOT EXISTS alerts (
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    predicted_failure_mode TEXT NOT NULL,
                    health_score REAL NOT NULL,
                    failure_probability REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_alerts_device_time
                ON alerts (device_id, timestamp);
                """
            )

    def insert_readings(self, readings: Iterable[TelemetryReading]) -> int:
        rows = [
            (
                reading.timestamp.isoformat(),
                reading.device_id,
                reading.health_score,
                reading.failure_probability,
                reading.predicted_failure_mode,
                reading.temperature,
                reading.pressure,
                reading.vibration,
                reading.rpm,
                reading.torque,
                reading.power_draw,
                reading.flow_rate,
                reading.voltage,
                reading.tool_wear,
            )
            for reading in readings
        ]
        if not rows:
            return 0
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO telemetry (
                    timestamp, device_id, health_score, failure_probability, predicted_failure_mode,
                    temperature, pressure, vibration, rpm, torque, power_draw, flow_rate, voltage, tool_wear
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def insert_alerts(self, alerts: Iterable[AlertRecord]) -> int:
        rows = [
            (
                alert.timestamp,
                alert.device_id,
                alert.severity,
                alert.title,
                alert.message,
                alert.predicted_failure_mode,
                alert.health_score,
                alert.failure_probability,
            )
            for alert in alerts
        ]
        if not rows:
            return 0
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO alerts (
                    timestamp, device_id, severity, title, message, predicted_failure_mode,
                    health_score, failure_probability
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def fetch_dataframe(self, query: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query, params).fetchall()]

    def latest_telemetry(self) -> list[dict[str, object]]:
        return self.fetch_dataframe(
            """
            SELECT t.*
            FROM telemetry t
            INNER JOIN (
                SELECT device_id, MAX(timestamp) AS max_timestamp
                FROM telemetry
                GROUP BY device_id
            ) latest
            ON t.device_id = latest.device_id AND t.timestamp = latest.max_timestamp
            ORDER BY failure_probability DESC
            """
        )

    def telemetry_for_device(self, device_id: str, hours: int = 24) -> list[dict[str, object]]:
        threshold = (datetime.now(timezone.utc) - timedelta(hours=hours)).replace(tzinfo=None).isoformat()
        return self.fetch_dataframe(
            """
            SELECT *
            FROM telemetry
            WHERE device_id = ?
              AND timestamp >= ?
            ORDER BY timestamp ASC
            """,
            (device_id, threshold),
        )

    def alert_history(self, limit: int = 200) -> list[dict[str, object]]:
        return self.fetch_dataframe(
            """
            SELECT *
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )

    def fleet_kpis(self) -> dict[str, float]:
        latest = self.latest_telemetry()
        if not latest:
            return {
                "devices": 0,
                "avg_health": 0.0,
                "critical_devices": 0,
                "warning_devices": 0,
                "avg_failure_probability": 0.0,
            }
        return {
            "devices": float(len(latest)),
            "avg_health": sum(row["health_score"] for row in latest) / len(latest),
            "critical_devices": float(sum(row["health_score"] < 0.30 for row in latest)),
            "warning_devices": float(sum(0.30 <= row["health_score"] < 0.60 for row in latest)),
            "avg_failure_probability": sum(row["failure_probability"] for row in latest) / len(latest),
        }
