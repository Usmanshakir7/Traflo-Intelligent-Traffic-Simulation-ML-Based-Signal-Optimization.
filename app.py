"""Traflo - Intelligent Traffic Simulation."""
import matplotlib.pyplot as plt
import streamlit as st

from controllers.fixed_time import FixedTimeController
from controllers.adaptive import AdaptiveController
from controllers.ml_controller import MLController
from core.engine import TrafficSimulation
from ui.controls import render_controls
from ui.dashboard import render_comparison
from ui.visualization import draw_intersection

st.set_page_config(
    page_title="Traflo | Traffic Simulator",
    page_icon="🚦",
    layout="wide",
)
st.title("Traflo")
st.caption("Stanford Code in Place X — Intelligent Traffic Simulation")
st.write(
    "Compare conventional fixed-time signals, rule-based adaptation, "
    "and a trained ML controller."
)

settings, run_clicked = render_controls()

if run_clicked:
    with st.spinner("Running all three controllers..."):
        try:
            fixed = TrafficSimulation(
                FixedTimeController(), **settings
            ).run(verbose=False)
            adaptive = TrafficSimulation(
                AdaptiveController(), **settings
            ).run(verbose=False)

            ml_controller = MLController(
                arrival_intervals=settings["arrival_intervals"]
            )
            ml = TrafficSimulation(
                ml_controller, **settings
            ).run(verbose=False)
            ml["decisions"] = ml_controller.decision_history

            assert fixed["arrived"] == adaptive["arrived"] == ml["arrived"]
        except Exception as error:
            st.error(f"Simulation failed: {error}")
            st.stop()

        st.session_state["traflo_results"] = {
            "fixed": fixed, "adaptive": adaptive, "ml": ml
        }
        st.session_state["traflo_settings"] = settings

if "traflo_results" not in st.session_state:
    st.info("Choose traffic settings in the sidebar, then click Run simulation.")
    st.stop()

results = st.session_state["traflo_results"]
if settings != st.session_state["traflo_settings"]:
    st.warning("Your inputs changed. Click Run simulation to update the results.")

sim_tab, compare_tab = st.tabs(["Intersection simulator", "Controller comparison"])

with sim_tab:
    selection = st.radio(
        "Controller",
        ["Fixed-Time", "Rule-Based Adaptive", "ML-Assisted"],
        horizontal=True,
    )
    selected_key = {
        "Fixed-Time": "fixed",
        "Rule-Based Adaptive": "adaptive",
        "ML-Assisted": "ml",
    }[selection]

    run = results[selected_key]
    second = st.slider(
        "Simulation time (seconds)", 1, len(run["history"]), 1
    )
    snapshot = run["history"][second - 1]

    graph, information = st.columns([2, 1])
    with graph:
        fig = draw_intersection(snapshot)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with information:
        st.metric("Signal", snapshot["signal"].replace("_", " "))
        st.metric("Vehicles waiting", snapshot["total_waiting"])
        st.metric("Vehicles passed", snapshot["total_departed"])
        st.write("**Queues by approach**")
        for road, count in snapshot["queues"].items():
            st.write(f"{road}: {count} cars")

    st.caption(
        "The slider displays recorded simulation states. "
        "Car icons represent queue samples, not individual vehicle positions."
    )

with compare_tab:
    render_comparison(results)
