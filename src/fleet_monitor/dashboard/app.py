"""Streamlit entrypoint for fleet-monitor."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from fleet_monitor.dashboard.data import DB_PATH


def main() -> None:
    st.set_page_config(
        page_title="Fleet Monitor",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Fleet Monitor")
    st.caption("Predictive maintenance dashboard for IoT device fleets across Kenya.")

    if not Path(DB_PATH).exists():
        st.warning(
            "No SQLite data found yet. Run `python scripts/seed_history.py` first, then refresh the app."
        )
    else:
        st.success(f"SQLite store detected at {DB_PATH}")

    st.markdown(
        """
        Use the sidebar to navigate between fleet health, device detail, model predictions,
        alert history, and performance diagnostics.
        """
    )


if __name__ == "__main__":
    main()

