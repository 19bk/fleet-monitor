"""Live prediction and explanation helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from fleet_monitor.ml.features import FEATURE_COLUMNS, build_live_feature_frame


FAILURE_MODE_COLUMNS = ["failure_twf", "failure_hdf", "failure_pwf", "failure_osf", "failure_rnf"]
FAILURE_MODE_LABELS = {
    "failure_twf": "Tool wear failure",
    "failure_hdf": "Heat dissipation failure",
    "failure_pwf": "Power failure",
    "failure_osf": "Overstrain failure",
    "failure_rnf": "Random failure",
}


def compute_health_score(record: dict[str, float | int | str]) -> float:
    score = 1.0
    score -= min(max((float(record["vibration"]) - 2.0) / 10.0, 0.0), 1.0) * 0.25
    score -= min(max((float(record["temperature"]) - 65.0) / 55.0, 0.0), 1.0) * 0.20
    score -= min(max((14.0 - float(record["flow_rate"])) / 14.0, 0.0), 1.0) * 0.15
    score -= min(max((2.2 - float(record["pressure"])) / 2.2, 0.0), 1.0) * 0.15
    score -= min(max((float(record["power_draw"]) - 980.0) / 1020.0, 0.0), 1.0) * 0.15
    score -= min(max((float(record["tool_wear"]) - 180.0) / 220.0, 0.0), 1.0) * 0.10
    return round(max(0.0, min(1.0, score)), 4)


def score_fleet_records(model_bundle: dict[str, Any], records: list[dict[str, Any]]) -> pd.DataFrame:
    feature_frame = build_live_feature_frame(records)
    features = feature_frame[FEATURE_COLUMNS]
    classifier = model_bundle["classifier"]
    failure_classifier = model_bundle["failure_mode_classifier"]
    probabilities = classifier.predict_proba(features)[:, 1]
    failure_modes = failure_classifier.predict(features)

    scored = pd.DataFrame.from_records(records)
    scored["health_score"] = scored.apply(compute_health_score, axis=1)
    scored["failure_probability"] = probabilities

    failure_mode_frame = pd.DataFrame(failure_modes, columns=FAILURE_MODE_COLUMNS)
    scored["predicted_failure_mode"] = failure_mode_frame.idxmax(axis=1).map(FAILURE_MODE_LABELS)
    scored.loc[failure_mode_frame.sum(axis=1) == 0, "predicted_failure_mode"] = "Normal operation"

    importances = _feature_importances(model_bundle)
    scored["top_risk_driver"] = features.apply(
        lambda row: explain_prediction(row, importances)["feature"],
        axis=1,
    )
    return scored


def _feature_importances(model_bundle: dict[str, Any]) -> dict[str, float]:
    model = model_bundle["classifier"]
    raw = getattr(model, "feature_importances_", None)
    if raw is None:
        return {feature: 1.0 / len(FEATURE_COLUMNS) for feature in FEATURE_COLUMNS}
    return dict(zip(FEATURE_COLUMNS, raw))


def explain_prediction(feature_row: pd.Series, importances: dict[str, float]) -> dict[str, Any]:
    weighted = {
        feature: abs(float(feature_row[feature])) * float(weight)
        for feature, weight in importances.items()
    }
    top_feature = max(weighted, key=weighted.get)
    return {
        "feature": top_feature,
        "importance": round(importances.get(top_feature, 0.0), 4),
        "value": round(float(feature_row[top_feature]), 4),
    }
