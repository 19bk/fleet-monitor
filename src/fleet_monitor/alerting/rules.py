"""Alert generation rules."""

from __future__ import annotations

from datetime import datetime

from fleet_monitor.storage.store import AlertRecord


def build_alerts(scored_rows: list[dict[str, object]]) -> list[AlertRecord]:
    alerts: list[AlertRecord] = []
    for row in scored_rows:
        health = float(row["health_score"])
        probability = float(row["failure_probability"])
        severity = None
        title = None
        message = None
        if health < 0.30 or probability > 0.80:
            severity = "critical"
            title = "Immediate maintenance required"
            message = (
                f"{row['device_id']} is at {health:.0%} health with {probability:.0%} failure risk. "
                f"Probable mode: {row['predicted_failure_mode']}."
            )
        elif health < 0.60 or probability > 0.55:
            severity = "warning"
            title = "Degradation detected"
            message = (
                f"{row['device_id']} is degrading. Health {health:.0%}, failure risk {probability:.0%}. "
                f"Top driver: {row.get('top_risk_driver', 'unknown')}."
            )
        elif float(row["tool_wear"]) > 180:
            severity = "info"
            title = "Maintenance window due"
            message = f"{row['device_id']} has elevated tool wear ({float(row['tool_wear']):.0f} min)."

        if severity is None:
            continue

        alerts.append(
            AlertRecord(
                timestamp=str(row.get("timestamp", datetime.utcnow().isoformat())),
                device_id=str(row["device_id"]),
                severity=severity,
                title=title,
                message=message,
                predicted_failure_mode=str(row["predicted_failure_mode"]),
                health_score=health,
                failure_probability=probability,
            )
        )
    return alerts

