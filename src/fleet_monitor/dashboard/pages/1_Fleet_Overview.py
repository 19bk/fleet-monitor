from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from fleet_monitor.dashboard.data import fleet_kpis, latest_telemetry_frame, load_config

try:
    import folium
    from streamlit_folium import st_folium
except Exception:  # pragma: no cover - optional dependency
    folium = None
    st_folium = None


st.set_page_config(page_title="Fleet Overview", layout="wide")
st.title("Fleet Overview")

frame = latest_telemetry_frame()
if frame.empty:
    st.info("No telemetry available yet. Seed the database first.")
    st.stop()

config_frame = pd.DataFrame(load_config()["devices"])
merged = frame.merge(config_frame, left_on="device_id", right_on="device_id", how="left")
kpis = fleet_kpis()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Devices", int(kpis["devices"]))
col2.metric("Avg health", f"{kpis['avg_health']:.0%}")
col3.metric("Critical", int(kpis["critical_devices"]))
col4.metric("Avg failure risk", f"{kpis['avg_failure_probability']:.0%}")

map_col, trend_col = st.columns([1.2, 1.8])
with map_col:
    st.subheader("Fleet Map")
    if folium is not None and st_folium is not None:
        fleet_map = folium.Map(location=[0.2, 37.8], zoom_start=6, tiles="CartoDB positron")
        for row in merged.to_dict(orient="records"):
            color = "red" if row["health_score"] < 0.3 else "orange" if row["health_score"] < 0.6 else "green"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=7,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=f"{row['name']} | health {row['health_score']:.0%}",
            ).add_to(fleet_map)
        st_folium(fleet_map, use_container_width=True, height=420)
    else:
        st.dataframe(merged[["device_id", "name", "county", "latitude", "longitude"]], use_container_width=True)

with trend_col:
    st.subheader("Risk Matrix")
    fig = px.scatter(
        merged,
        x="health_score",
        y="failure_probability",
        color="predicted_failure_mode",
        size="tool_wear",
        hover_name="name",
        text="device_id",
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Device Table")
st.dataframe(
    merged[
        [
            "device_id",
            "name",
            "device_type",
            "county",
            "health_score",
            "failure_probability",
            "predicted_failure_mode",
            "temperature",
            "vibration",
            "tool_wear",
        ]
    ].sort_values(["failure_probability", "health_score"], ascending=[False, True]),
    use_container_width=True,
)

