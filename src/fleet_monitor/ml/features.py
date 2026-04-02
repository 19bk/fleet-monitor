"""Feature engineering for AI4I model training and live scoring."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd


RAW_TO_FEATURE_MAP = {
    "Air temperature [K]": "air_temperature_k",
    "Process temperature [K]": "process_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Type": "product_type",
    "Machine failure": "machine_failure",
    "TWF": "failure_twf",
    "HDF": "failure_hdf",
    "PWF": "failure_pwf",
    "OSF": "failure_osf",
    "RNF": "failure_rnf",
    "\ufeffUDI": "udi",
    "Product ID": "product_id",
}

FEATURE_COLUMNS = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
    "type_l",
    "type_m",
    "type_h",
    "temp_diff_k",
    "power_estimate",
    "strain_index",
    "speed_deviation",
    "wear_per_torque",
    "temp_x_torque",
]


def load_ai4i_dataset(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    return frame.rename(columns=RAW_TO_FEATURE_MAP)


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["temp_diff_k"] = enriched["process_temperature_k"] - enriched["air_temperature_k"]
    enriched["power_estimate"] = enriched["rotational_speed_rpm"] * enriched["torque_nm"] / 9549.0
    enriched["strain_index"] = enriched["tool_wear_min"] * enriched["torque_nm"] / 100.0
    enriched["speed_deviation"] = (enriched["rotational_speed_rpm"] - enriched["rotational_speed_rpm"].median()).abs()
    enriched["wear_per_torque"] = enriched["tool_wear_min"] / enriched["torque_nm"].clip(lower=0.1)
    enriched["temp_x_torque"] = enriched["temp_diff_k"] * enriched["torque_nm"]

    type_dummies = pd.get_dummies(enriched["product_type"].str.lower(), prefix="type")
    for column in ["type_l", "type_m", "type_h"]:
        enriched[column] = type_dummies.get(column, 0)

    return enriched


def build_training_matrices(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    enriched = engineer_features(frame)
    x = enriched[FEATURE_COLUMNS].copy()
    y = enriched["machine_failure"].astype(int)
    failure_modes = enriched[["failure_twf", "failure_hdf", "failure_pwf", "failure_osf", "failure_rnf"]].astype(int)
    return x, y, failure_modes


def build_live_feature_frame(records: Sequence[dict[str, float | int | str]]) -> pd.DataFrame:
    frame = pd.DataFrame.from_records(records)
    frame = frame.rename(
        columns={
            "temperature": "process_temperature_k",
            "temperature_ambient": "air_temperature_k",
            "rpm": "rotational_speed_rpm",
            "torque": "torque_nm",
            "tool_wear": "tool_wear_min",
            "device_type": "product_type",
        }
    )
    if "air_temperature_k" not in frame:
        frame["air_temperature_k"] = frame["process_temperature_k"] - 8.0
    return engineer_features(frame)

