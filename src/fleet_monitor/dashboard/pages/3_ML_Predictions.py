from __future__ import annotations

import plotly.express as px
import streamlit as st

from fleet_monitor.dashboard.data import latest_telemetry_frame


st.set_page_config(page_title="ML Predictions", layout="wide")
st.title("ML Predictions")

frame = latest_telemetry_frame()
if frame.empty:
    st.info("No telemetry available yet.")
    st.stop()

frame = frame.copy()
frame["estimated_rul_days"] = ((frame["health_score"].clip(lower=0.05) / frame["failure_probability"].clip(lower=0.05)) * 7).round(1)
frame["risk_band"] = frame["failure_probability"].apply(
    lambda value: "Critical" if value > 0.8 else "Warning" if value > 0.55 else "Monitor"
)

col1, col2 = st.columns([1.5, 1])
with col1:
    st.subheader("Failure Forecast")
    st.dataframe(
        frame[
            [
                "device_id",
                "health_score",
                "failure_probability",
                "predicted_failure_mode",
                "estimated_rul_days",
                "risk_band",
            ]
        ].sort_values("failure_probability", ascending=False),
        use_container_width=True,
    )
with col2:
    st.subheader("RUL Distribution")
    st.plotly_chart(px.histogram(frame, x="estimated_rul_days", nbins=10), use_container_width=True)

st.subheader("Risk Scatter")
st.plotly_chart(
    px.scatter(
        frame,
        x="tool_wear",
        y="failure_probability",
        color="risk_band",
        hover_name="device_id",
        size="temperature",
    ),
    use_container_width=True,
)

