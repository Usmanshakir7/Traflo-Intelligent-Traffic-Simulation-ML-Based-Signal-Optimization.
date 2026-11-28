
"""Traflo interactive traffic simulation app."""

import matplotlib.pyplot as plt
import streamlit as st

from controllers.fixed_time import FixedTimeController
from controllers.adaptive import AdaptiveController
from core.engine import TrafficSimulation
from ui.controls import render_controls
from ui.dashboard import render_comparison
from ui.visualization import draw_intersection

st.set_page_config(page_title="Traflo | Traffic Simulator", page_icon="🚦", layout="wide")

st.title("Traflo")
st.caption("Stanford Code in Place X — Interactive Traffic Simulation & Signal Optimization")
st.write(
    "Explore a four-way intersection, customize traffic conditions, and compare a "
    "conventional fixed-time signal with a rule-based adaptive controller."
)

settings, run_clicked = render_controls()

if run_clicked:
    with st.spinner("Running both traffic simulations..."):
        fixed = TrafficSimulation(FixedTimeController(), **settings).run(verbose=False)
        adaptive = TrafficSimulation(AdaptiveController(), **settings).run(verbose=False)
        st.session_state["traflo_results"] = {"fixed": fixed, "adaptive": adaptive}
        st.session_state["traflo_settings"] = settings

if "traflo_results" not in st.session_state:
    st.info("Choose a scenario in the left sidebar, then click **Run simulation**.")
    st.stop()

results = st.session_state["traflo_results"]
last_settings = st.session_state["traflo_settings"]
if settings != last_settings:
    st.warning("Settings have changed. Click **Run simulation** to update the results.")

sim_tab, compare_tab = st.tabs(["Intersection simulator", "Controller comparison"])

with sim_tab:
    st.subheader("Explore a simulation step")
    controller_name = st.radio(
        "Traffic controller", ["Fixed-time", "Adaptive"], horizontal=True
    )
    key = "fixed" if controller_name == "Fixed-time" else "adaptive"
    run = results[key]
    selected_second = st.slider(
        "Simulation time (seconds)", 1, len(run["history"]), 1
    )
    snapshot = run["history"][selected_second - 1]

    figure_col, stats_col = st.columns([2, 1])
    with figure_col:
        fig = draw_intersection(snapshot)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with stats_col:
        st.metric("Signal", snapshot["signal"].replace("_", " "))
        st.metric("Vehicles waiting", snapshot["total_waiting"])
        st.metric("Vehicles passed so far", snapshot["total_departed"])
        st.write("**Current queues**")
        for road, count in snapshot["queues"].items():
            st.write(f"{road}: {count} vehicles")
    st.caption(
        "Move the time slider to inspect recorded simulation states. The car icons are "
        "queue indicators, not GPS positions or smooth real-time animations."
    )

with compare_tab:
    render_comparison(results["fixed"], results["adaptive"])
