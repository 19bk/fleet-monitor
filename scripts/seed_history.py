#!/usr/bin/env python3
"""Generate historical telemetry and alerts into SQLite."""

from __future__ import annotations

from pathlib import Path

from fleet_monitor.alerting.rules import build_alerts
from fleet_monitor.ml.predict import score_fleet_records
from fleet_monitor.ml.train import load_model_bundle, train_model_bundle
from fleet_monitor.simulator.fleet import FleetSimulator
from fleet_monitor.storage.store import FleetStore


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    artifact_dir = repo_root / "artifacts"
    if not (artifact_dir / "model_bundle.joblib").exists():
        train_model_bundle(repo_root / "data" / "ai4i2020.csv", artifact_dir)

    model_bundle = load_model_bundle(artifact_dir)
    simulator = FleetSimulator.from_config(repo_root / "data" / "fleet_config.json")
    store = FleetStore(repo_root / "data" / "fleet_monitor.db")
    store.initialize()

    readings = simulator.generate_history(days=30, interval_minutes=60)
    store.insert_readings(readings)

    latest_records = [reading.as_record() | {"device_type": "M"} for reading in readings[-len(simulator.devices):]]
    scored = score_fleet_records(model_bundle, latest_records)
    store.insert_alerts(build_alerts(scored.to_dict(orient="records")))

    print(f"Seeded {len(readings)} telemetry rows into {store.db_path}")


if __name__ == "__main__":
    main()

