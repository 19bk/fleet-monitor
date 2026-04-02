from __future__ import annotations

import plotly.express as px
import streamlit as st

from fleet_monitor.dashboard.data import alert_history_frame


st.set_page_config(page_title="Alert History", layout="wide")
st.title("Alert History")

alerts = alert_history_frame()
if alerts.empty:
    st.info("No alerts recorded yet.")
    st.stop()

col1, col2 = st.columns([1.2, 1])
with col1:
    st.dataframe(alerts, use_container_width=True)
with col2:
    severity_counts = alerts["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "count"]
    st.plotly_chart(px.bar(severity_counts, x="severity", y="count", color="severity"), use_container_width=True)

