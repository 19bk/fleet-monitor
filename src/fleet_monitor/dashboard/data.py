"""Shared dashboard data access helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from fleet_monitor.ml.evaluate import summarize_model_performance
from fleet_monitor.ml.train import load_model_bundle
from fleet_monitor.storage.store import FleetStore


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
ARTIFACT_DIR = REPO_ROOT / "artifacts"
DB_PATH = DATA_DIR / "fleet_monitor.db"
CONFIG_PATH = DATA_DIR / "fleet_config.json"
AI4I_PATH = DATA_DIR / "ai4i2020.csv"


def get_store() -> FleetStore:
    store = FleetStore(DB_PATH)
    store.initialize()
    return store


def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def latest_telemetry_frame() -> pd.DataFrame:
    return pd.DataFrame(get_store().latest_telemetry())


def device_history_frame(device_id: str, hours: int = 24) -> pd.DataFrame:
    return pd.DataFrame(get_store().telemetry_for_device(device_id, hours=hours))


def alert_history_frame(limit: int = 200) -> pd.DataFrame:
    return pd.DataFrame(get_store().alert_history(limit=limit))


def fleet_kpis() -> dict[str, float]:
    return get_store().fleet_kpis()


def model_bundle_or_none() -> dict[str, Any] | None:
    bundle_path = ARTIFACT_DIR / "model_bundle.joblib"
    if not bundle_path.exists():
        return None
    return load_model_bundle(ARTIFACT_DIR)


def model_performance_or_none() -> dict[str, Any] | None:
    bundle = model_bundle_or_none()
    if bundle is None:
        return None
    return summarize_model_performance(bundle, str(AI4I_PATH))

