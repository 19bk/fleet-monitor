"""Training utilities for predictive maintenance models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier

from fleet_monitor.ml.features import FEATURE_COLUMNS, build_training_matrices, load_ai4i_dataset

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - optional dependency
    XGBClassifier = None


@dataclass
class TrainingArtifacts:
    feature_columns: list[str]
    primary_model_name: str
    metrics: dict[str, Any]
    classifier: Any
    baseline_classifier: Any
    failure_mode_classifier: Any

    def save(self, output_dir: str | Path) -> None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "feature_columns": self.feature_columns,
                "primary_model_name": self.primary_model_name,
                "metrics": self.metrics,
                "classifier": self.classifier,
                "baseline_classifier": self.baseline_classifier,
                "failure_mode_classifier": self.failure_mode_classifier,
            },
            output_path / "model_bundle.joblib",
        )


def _build_primary_classifier() -> tuple[str, Any]:
    if XGBClassifier is not None:
        return (
            "xgboost",
            XGBClassifier(
                n_estimators=220,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                scale_pos_weight=28.0,
                eval_metric="logloss",
                random_state=42,
            ),
        )
    return (
        "gradient_boosting_fallback",
        GradientBoostingClassifier(random_state=42),
    )


def train_model_bundle(data_path: str | Path, output_dir: str | Path) -> TrainingArtifacts:
    raw = load_ai4i_dataset(data_path)
    x, y, failure_modes = build_training_matrices(raw)
    x_train, x_test, y_train, y_test, fm_train, fm_test = train_test_split(
        x,
        y,
        failure_modes,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    baseline = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
    )
    baseline.fit(x_train, y_train)

    primary_name, primary = _build_primary_classifier()
    primary.fit(x_train, y_train)

    failure_mode_model = MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators=160,
            max_depth=9,
            class_weight="balanced_subsample",
            random_state=42,
        )
    )
    failure_mode_model.fit(x_train, fm_train)

    baseline_scores = baseline.predict_proba(x_test)[:, 1]
    primary_scores = primary.predict_proba(x_test)[:, 1]
    baseline_preds = (baseline_scores >= 0.5).astype(int)
    primary_preds = (primary_scores >= 0.5).astype(int)

    metrics = {
        "baseline": {
            "roc_auc": float(roc_auc_score(y_test, baseline_scores)),
            "average_precision": float(average_precision_score(y_test, baseline_scores)),
            "f1": float(f1_score(y_test, baseline_preds)),
        },
        "primary": {
            "name": primary_name,
            "roc_auc": float(roc_auc_score(y_test, primary_scores)),
            "average_precision": float(average_precision_score(y_test, primary_scores)),
            "f1": float(f1_score(y_test, primary_preds)),
        },
        "class_balance": {
            "failure_rate": float(y.mean()),
            "rows": int(len(raw)),
            "features": len(FEATURE_COLUMNS),
        },
    }

    artifacts = TrainingArtifacts(
        feature_columns=FEATURE_COLUMNS,
        primary_model_name=primary_name,
        metrics=metrics,
        classifier=primary,
        baseline_classifier=baseline,
        failure_mode_classifier=failure_mode_model,
    )
    artifacts.save(output_dir)
    return artifacts


def load_model_bundle(model_dir: str | Path) -> dict[str, Any]:
    return joblib.load(Path(model_dir) / "model_bundle.joblib")

