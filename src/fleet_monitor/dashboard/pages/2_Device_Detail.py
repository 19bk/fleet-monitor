from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fleet_monitor.dashboard.data import device_history_frame, latest_telemetry_frame


st.set_page_config(page_title="Device Detail", layout="wide")
st.title("Device Detail")

latest = latest_telemetry_frame()
if latest.empty:
    st.info("No telemetry available yet.")
    st.stop()

device_id = st.selectbox("Select device", options=latest["device_id"].sort_values().tolist())
device_latest = latest.loc[latest["device_id"] == device_id].iloc[0]
history = device_history_frame(device_id, hours=24)

metric_col, gauge_col = st.columns([1, 1.4])
with metric_col:
    st.metric("Health", f"{device_latest['health_score']:.0%}")
    st.metric("Failure risk", f"{device_latest['failure_probability']:.0%}")
    st.metric("Failure mode", str(device_latest["predicted_failure_mode"]))
    st.metric("Tool wear", f"{float(device_latest['tool_wear']):.0f} min")

with gauge_col:
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(device_latest["health_score"]) * 100,
            title={"text": "Health score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#f97316"},
                "steps": [
                    {"range": [0, 30], "color": "#fecaca"},
                    {"range": [30, 60], "color": "#fed7aa"},
                    {"range": [60, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    st.plotly_chart(gauge, use_container_width=True)

if history.empty:
    st.warning("No 24h history found for this device.")
    st.stop()

sensor_cols = ["temperature", "pressure", "vibration", "rpm", "torque", "power_draw", "flow_rate", "voltage", "tool_wear"]
long_frame = history.melt(id_vars=["timestamp"], value_vars=sensor_cols, var_name="sensor", value_name="value")
fig = px.line(long_frame, x="timestamp", y="value", color="sensor")
st.plotly_chart(fig, use_container_width=True)

