from fleet_monitor.alerting.rules import build_alerts


def test_build_alerts_creates_critical_alert() -> None:
    alerts = build_alerts(
        [
            {
                "timestamp": "2026-01-01T00:00:00",
                "device_id": "dev_001",
                "health_score": 0.22,
                "failure_probability": 0.91,
                "predicted_failure_mode": "Power failure",
                "top_risk_driver": "power_estimate",
                "tool_wear": 210,
            }
        ]
    )
    assert len(alerts) == 1
    assert alerts[0].severity == "critical"

