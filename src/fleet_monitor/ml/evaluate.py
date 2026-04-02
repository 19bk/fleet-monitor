"""Model evaluation helpers used by scripts and dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, roc_curve

from fleet_monitor.ml.features import build_training_matrices, load_ai4i_dataset


def summarize_model_performance(model_bundle: dict[str, Any], data_path: str) -> dict[str, Any]:
    raw = load_ai4i_dataset(data_path)
    x, y, failure_modes = build_training_matrices(raw)
    classifier = model_bundle["classifier"]
    failure_classifier = model_bundle["failure_mode_classifier"]

    probabilities = classifier.predict_proba(x)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    matrix = confusion_matrix(y, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(y, predictions, average="binary")
    fpr, tpr, _ = roc_curve(y, probabilities)

    failure_predictions = failure_classifier.predict(x)
    failure_frame = pd.DataFrame(
        failure_predictions,
        columns=["TWF", "HDF", "PWF", "OSF", "RNF"],
    )

    return {
        "confusion_matrix": matrix.tolist(),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
        "failure_mode_positive_counts": failure_frame.sum().to_dict(),
        "saved_metrics": model_bundle["metrics"],
    }

