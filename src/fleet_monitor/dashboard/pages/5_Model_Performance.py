from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fleet_monitor.dashboard.data import model_bundle_or_none, model_performance_or_none


st.set_page_config(page_title="Model Performance", layout="wide")
st.title("Model Performance")

bundle = model_bundle_or_none()
performance = model_performance_or_none()
if bundle is None or performance is None:
    st.info("Train the model first with `python scripts/train_model.py`.")
    st.stop()

saved_metrics = performance["saved_metrics"]
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Primary model", saved_metrics["primary"]["name"])
metric_col2.metric("ROC AUC", f"{saved_metrics['primary']['roc_auc']:.3f}")
metric_col3.metric("F1", f"{saved_metrics['primary']['f1']:.3f}")

matrix = pd.DataFrame(performance["confusion_matrix"], columns=["Pred 0", "Pred 1"], index=["True 0", "True 1"])
st.subheader("Confusion Matrix")
st.dataframe(matrix, use_container_width=True)

roc = performance["roc_curve"]
fig = go.Figure()
fig.add_trace(go.Scatter(x=roc["fpr"], y=roc["tpr"], mode="lines", name="ROC"))
fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Chance", line={"dash": "dash"}))
st.plotly_chart(fig, use_container_width=True)

importances = getattr(bundle["classifier"], "feature_importances_", None)
if importances is not None:
    importance_frame = pd.DataFrame(
        {"feature": bundle["feature_columns"], "importance": importances}
    ).sort_values("importance", ascending=False)
    st.subheader("Feature Importance")
    st.plotly_chart(px.bar(importance_frame, x="importance", y="feature", orientation="h"), use_container_width=True)

mode_counts = pd.DataFrame(
    list(performance["failure_mode_positive_counts"].items()),
    columns=["mode", "positive_predictions"],
)
st.subheader("Failure Mode Coverage")
st.plotly_chart(px.bar(mode_counts, x="mode", y="positive_predictions"), use_container_width=True)

