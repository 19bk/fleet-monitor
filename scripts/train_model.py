#!/usr/bin/env python3
"""Train predictive maintenance models from the AI4I dataset."""

from __future__ import annotations

from pathlib import Path

from fleet_monitor.ml.train import train_model_bundle


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    artifacts = train_model_bundle(
        data_path=repo_root / "data" / "ai4i2020.csv",
        output_dir=repo_root / "artifacts",
    )
    print("Primary model:", artifacts.primary_model_name)
    print("Metrics:", artifacts.metrics)


if __name__ == "__main__":
    main()

