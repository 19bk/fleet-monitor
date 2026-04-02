#!/usr/bin/env python3
"""Run a short live simulation loop and write rows to SQLite."""

from __future__ import annotations

from datetime import datetime
import time
from pathlib import Path

from fleet_monitor.simulator.fleet import FleetSimulator
from fleet_monitor.storage.store import FleetStore


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    simulator = FleetSimulator.from_config(repo_root / "data" / "fleet_config.json")
    store = FleetStore(repo_root / "data" / "fleet_monitor.db")
    store.initialize()

    print("Running live fleet simulator. Ctrl+C to stop.")
    try:
        while True:
            readings = simulator.tick(timestamp=datetime.utcnow(), interval_minutes=5)
            inserted = store.insert_readings(readings)
            print(f"{datetime.utcnow().isoformat()} inserted {inserted} rows")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
